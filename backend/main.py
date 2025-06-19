from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional
import tempfile
import subprocess
import os
import json
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from langchain_community.llms import Ollama
import chromadb
from sentence_transformers import SentenceTransformer
import yaml

app = FastAPI(title="Generador de informes IA")

# Instancia global del modelo para reutilizar conexiones
llm = Ollama(model="mixtral")


HIST_PATH = Path(__file__).with_name("historial.json")
CHROMA_PATH = Path(__file__).with_name("chroma_db")

# Cargar configuración global
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.yaml"
if CONFIG_PATH.exists():
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        CONFIG = yaml.safe_load(fh) or {}
else:
    CONFIG = {}

EXPORT_DIR = Path(CONFIG.get("export_dir", "exports"))
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Inicializar modelo de embedding y base vectorial persistente
embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = client.get_or_create_collection("informes")


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
    try:
        existing = collection.get(ids=[item["id"]])
        if existing and existing.get("ids"):
            return
    except Exception:
        pass
    emb = embedder.encode(item["contenido"]).tolist()
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
    try:
        collection.delete(ids=[item_id])
    except Exception:
        pass


def sync_chroma() -> None:
    """Sincroniza la base vectorial con el historial guardado."""
    historial = cargar_historial()
    for it in historial:
        agregar_a_chroma(it)

def generar_contenido(tema: str, tipo: str) -> str:
    """Genera un informe usando LangChain + Ollama."""
    prompt = (
        f"Redacta un informe profesional tipo \"{tipo}\" sobre el tema: \"{tema}\". "
        "Incluye introducci\u00f3n, desarrollo argumental y conclusiones."
    )
    return llm(prompt)


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


class ExportarRequest(BaseModel):
    contenido: str
    formato: str

@app.post("/generar")
async def generar(req: GenerarRequest):
    """Genera un informe real usando LangChain y Ollama."""
    if not req.tema:
        raise HTTPException(status_code=400, detail="Tema es requerido")

    contenido = generar_contenido(req.tema, req.tipo)
    informe = {
        "id": str(uuid4()),
        "tema": req.tema,
        "tipo": req.tipo,
        "contenido": contenido,
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
    emb = embedder.encode(req.query).tolist()
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
