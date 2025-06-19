from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import tempfile
import subprocess
import os
import json
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
try:
    from langchain_community.llms import Ollama
    from langchain_community.llms.ollama import OllamaEndpointNotFoundError
except Exception:  # pragma: no cover - optional dependency
    Ollama = None
    OllamaEndpointNotFoundError = Exception
try:
    import chromadb
except Exception:  # pragma: no cover - optional dependency
    chromadb = None
try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None
import yaml
from threading import Lock


app = FastAPI(title="Generador de informes IA")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:1420", "http://localhost:1420"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REPO_ROOT = Path(__file__).resolve().parents[1]
HIST_PATH = REPO_ROOT / "historial.json"
CHROMA_PATH = REPO_ROOT / "chroma_db"

# Cargar configuración global
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.yaml"
if CONFIG_PATH.exists():
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        CONFIG = yaml.safe_load(fh) or {}
else:
    CONFIG = {}

# Instancia global del modelo para reutilizar conexiones
MODEL_NAME = CONFIG.get("model", "mixtral")
llm = Ollama(model=MODEL_NAME) if Ollama else None

EXPORT_DIR = Path(CONFIG.get("export_dir", "exports"))
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Inicializar modelo de embedding y base vectorial persistente
if SentenceTransformer:
    try:
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:  # pragma: no cover - handle offline env
        class _DummyEmbedder:
            def encode(self, text):
                return [0.0]

        embedder = _DummyEmbedder()
else:
    class _DummyEmbedder:
        def encode(self, text):
            return [0.0]

    embedder = _DummyEmbedder()
client = chromadb.PersistentClient(path=str(CHROMA_PATH)) if chromadb else None
collection = client.get_or_create_collection("informes") if client else None


def cargar_historial() -> list:
    if HIST_PATH.exists():
        with HIST_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    return []


def guardar_historial(items: list) -> None:
    with HIST_PATH.open("w", encoding="utf-8") as fh:
        json.dump(items, fh, ensure_ascii=False, indent=2)


def agregar_a_chroma(item: dict) -> None:
    """Guarda el embedding de un informe en ChromaDB."""
    if not collection or not embedder:
        return
    try:
        existing = collection.get(ids=[item["id"]])
        if existing and existing.get("ids"):
            return
    except Exception:
        pass
    emb_raw = embedder.encode(item["contenido"])
    emb = emb_raw.tolist() if hasattr(emb_raw, "tolist") else emb_raw
    collection.add(
        ids=[item["id"]],
        embeddings=[emb],
        metadatas=[{
            "tema": item["tema"],
            "tipo": item["tipo"],
            "timestamp": item["timestamp"],
        }],
    )


def eliminar_de_chroma(item_id: str) -> None:
    """Elimina un embedding de la base vectorial si existe."""
    if not collection:
        return
    try:
        collection.delete(ids=[item_id])
    except Exception:
        pass


def sync_chroma() -> None:
    """Sincroniza la base vectorial con el historial guardado."""
    if not collection or not embedder:
        return
    historial = cargar_historial()
    for it in historial:
        agregar_a_chroma(it)

# --- Conversación Asistente Curioso ---
class EstadoConversacion(BaseModel):
    paso: int = 0
    proposito: str | None = None
    tema: str | None = None
    estilo: str | None = None
    paginas: int | None = None
    extras: str | None = None


_convs: dict[str, EstadoConversacion] = {}
_conv_lock = Lock()


class Mensaje(BaseModel):
    mensaje: str


def _iniciar_conv() -> str:
    return "¿Para qué necesitas este informe?"


@app.post("/asistente/{conv_id}")
async def asistente(conv_id: str, msg: Mensaje):
    """Conversación paso a paso para recolectar contexto."""
    with _conv_lock:
        estado = _convs.get(conv_id)
        if estado is None:
            estado = EstadoConversacion()
            _convs[conv_id] = estado
            return {"reply": _iniciar_conv()}

        texto = msg.mensaje.strip()
        if estado.paso == 0:
            estado.proposito = texto
            estado.paso = 1
            return {
                "reply": "¿Sobre qué tema específico trata el informe?"
            }
        if estado.paso == 1:
            estado.tema = texto
            estado.paso = 2
            return {
                "reply": "¿Qué estilo prefieres (técnico, académico, ejecutivo, etc.)?"
            }
        if estado.paso == 2:
            estado.estilo = texto
            estado.paso = 3
            return {"reply": "¿Cuántas páginas deseas? (máximo 30)"}
        if estado.paso == 3:
            try:
                num = int(texto.split()[0])
            except Exception:
                return {
                    "reply": "Indica un número de páginas válido entre 1 y 30."}
            if num < 1 or num > 30:
                return {"reply": "El número debe estar entre 1 y 30."}
            estado.paginas = num
            estado.paso = 4
            return {
                "reply": "¿Hay fuentes, restricciones o tono específico que debamos considerar?"
            }
        if estado.paso == 4:
            estado.extras = texto
            estado.paso = 5
            return {"reply": "Contexto completado", "contexto": estado.dict()}

    return {"reply": "Conversación finalizada"}

def generar_contenido(
    tema: str,
    tipo: str,
    proposito: str | None = None,
    estilo: str | None = None,
    paginas: int | None = None,
    extras: str | None = None,
) -> str:
    """Genera un informe usando LangChain + Ollama."""
    if llm is None:
        raise HTTPException(status_code=500, detail="Modelo Ollama no disponible")
    prompt = (
        f"Redacta un informe profesional en espa\u00f1ol tipo \"{tipo}\" sobre el tema: \"{tema}\". "
        f"Prop\u00f3sito: {proposito or 'N/A'}. "
        f"Estilo: {estilo or 'est\u00e1ndar'}. "
        f"Extensi\u00f3n aproximada: {paginas or '5'} p\u00e1ginas. "
        "Incluye introducci\u00f3n, desarrollo argumental y conclusiones. "
        f"Consideraciones adicionales: {extras or 'ninguna'}."
    )
    try:
        return llm(prompt)
    except OllamaEndpointNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="Modelo Mixtral no encontrado. Ejecute `ollama pull mixtral`",
        ) from exc


def exportar_a_archivo(contenido: str, formato: str) -> str:
    """Convierte el contenido a DOCX o PDF usando pandoc."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8") as tmp_md:
        tmp_md.write(contenido)
        md_path = tmp_md.name

    ext = ".docx" if formato == "docx" else ".pdf"
    out_name = f"{Path(md_path).stem}{ext}"
    out_path = EXPORT_DIR / out_name

    pandoc_cmd = ["pandoc", md_path, "-o", str(out_path)]
    if formato == "docx" and CONFIG.get("docx_template"):
        pandoc_cmd.extend(["--reference-doc", CONFIG["docx_template"]])
    if formato == "pdf" and CONFIG.get("pdf_css"):
        pandoc_cmd.extend(["-c", CONFIG["pdf_css"]])

    try:
        subprocess.run(pandoc_cmd, check=True)
    except subprocess.CalledProcessError as exc:
        os.remove(md_path)
        raise HTTPException(status_code=500, detail="Error al exportar") from exc

    os.remove(md_path)
    return str(out_path)

class GenerarRequest(BaseModel):
    tema: str
    tipo: str
    proposito: str | None = None
    estilo: str | None = None
    paginas: int | None = None
    extras: str | None = None


class ExportarRequest(BaseModel):
    contenido: str
    formato: str

@app.post("/generar")
async def generar(req: GenerarRequest):
    """Genera un informe real usando LangChain y Ollama."""
    if not req.tema:
        raise HTTPException(status_code=400, detail="Tema es requerido")

    contenido = generar_contenido(
        req.tema,
        req.tipo,
        proposito=req.proposito,
        estilo=req.estilo,
        paginas=req.paginas,
        extras=req.extras,
    )
    informe = {
        "id": str(uuid4()),
        "tema": req.tema,
        "tipo": req.tipo,
        "contenido": contenido,
        "proposito": req.proposito,
        "estilo": req.estilo,
        "paginas": req.paginas,
        "extras": req.extras,
        "timestamp": datetime.now().isoformat(),
    }
    historial = cargar_historial()
    historial.append(informe)
    guardar_historial(historial)
    agregar_a_chroma(informe)
    return {"id": informe["id"], "contenido": contenido}


@app.post("/exportar")
async def exportar(req: ExportarRequest, background_tasks: BackgroundTasks):
    """Convierte el texto generado a DOCX o PDF y lo devuelve."""
    if req.formato not in {"docx", "pdf"}:
        raise HTTPException(status_code=400, detail="Formato no soportado")
    if not req.contenido:
        raise HTTPException(status_code=400, detail="Contenido vac\u00edo")

    file_path = exportar_a_archivo(req.contenido, req.formato)
    if not os.path.exists(file_path):
        Path(file_path).touch()
    background_tasks.add_task(os.remove, file_path)
    media = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if req.formato == "docx"
        else "application/pdf"
    )
    return FileResponse(file_path, media_type=media, filename=f"informe.{req.formato}", background=background_tasks)


@app.get("/historial")
async def listar_historial():
    """Devuelve la lista de informes guardados (sin contenido)."""
    historial = cargar_historial()
    return [
        {
            "id": item["id"],
            "tema": item["tema"],
            "tipo": item["tipo"],
            "timestamp": item["timestamp"],
        }
        for item in historial
    ]


@app.get("/historial/{item_id}")
async def obtener_informe(item_id: str, background_tasks: BackgroundTasks, exportar: Optional[str] = None):
    """Obtiene un informe completo por ID o lo exporta en el formato indicado."""
    historial = cargar_historial()
    for item in historial:
        if item["id"] == item_id:
            if exportar:
                if exportar not in {"docx", "pdf"}:
                    raise HTTPException(status_code=400, detail="Formato no soportado")
                file_path = exportar_a_archivo(item["contenido"], exportar)
                if background_tasks:
                    background_tasks.add_task(os.remove, file_path)
                media = (
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    if exportar == "docx"
                    else "application/pdf"
                )
                return FileResponse(
                    file_path,
                    media_type=media,
                    filename=f"informe.{exportar}",
                    background=background_tasks,
                )
            return item
    raise HTTPException(status_code=404, detail="Informe no encontrado")


@app.delete("/historial/{item_id}")
async def eliminar_informe(item_id: str):
    """Elimina un informe del historial."""
    historial = cargar_historial()
    nuevo_historial = [it for it in historial if it["id"] != item_id]
    if len(nuevo_historial) == len(historial):
        raise HTTPException(status_code=404, detail="Informe no encontrado")
    guardar_historial(nuevo_historial)
    eliminar_de_chroma(item_id)
    return {"ok": True}


class BuscarRequest(BaseModel):
    query: str
    k: int = 5


@app.post("/buscar")
async def buscar(req: BuscarRequest):
    """Busca informes similares a la consulta."""
    if not req.query:
        raise HTTPException(status_code=400, detail="Consulta vac\u00eda")
    emb_raw = embedder.encode(req.query)
    emb = emb_raw.tolist() if hasattr(emb_raw, "tolist") else emb_raw
    try:
        result = collection.query(
            query_embeddings=[emb],
            n_results=req.k,
            include=["metadatas", "ids"],
        )
    except Exception:
        return []

    hist_map = {item["id"]: item for item in cargar_historial()}
    items = []
    ids = result.get("ids", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    for rid, meta in zip(ids, metas):
        if rid in hist_map:
            base = hist_map[rid]
            items.append(
                {
                    "id": rid,
                    "tema": meta.get("tema", base["tema"]),
                    "tipo": meta.get("tipo", base["tipo"]),
                    "timestamp": meta.get("timestamp", base["timestamp"]),
                    "snippet": base.get("contenido", "")[:200],
                }
            )
    return items


# Sincronizar la base vectorial al iniciar el servidor
sync_chroma()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
