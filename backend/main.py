from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Request
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import tempfile
import subprocess
import os
import json
import asyncio
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parent))
    from document_generator import crear_docx
else:
    from .document_generator import crear_docx
try:
    from langchain_ollama import OllamaLLM
except Exception:  # pragma: no cover - optional dependency
    OllamaLLM = None
try:
    from langchain_community.llms.ollama import OllamaEndpointNotFoundError
except Exception:  # pragma: no cover - optional dependency
    OllamaEndpointNotFoundError = Exception
try:
    import chromadb
except Exception:  # pragma: no cover - optional dependency
    chromadb = None
try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None
try:
    from langdetect import detect
except Exception:  # pragma: no cover - optional dependency
    detect = None
try:
    import pdfplumber
except Exception:  # pragma: no cover - optional dependency
    pdfplumber = None
try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover - optional dependency
    fitz = None
try:
    from docx import Document
except Exception:  # pragma: no cover - optional dependency
    Document = None
import yaml
from threading import Lock
import re
import shutil
import unicodedata


class Utf8JSONResponse(JSONResponse):
    """JSONResponse con codificación UTF-8 explícita."""

    media_type = "application/json; charset=utf-8"


app = FastAPI(title="Generador de informes IA", default_response_class=Utf8JSONResponse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:1420", "http://localhost:1420"],
    allow_methods=["*"],
    allow_headers=["*"],
)

REPO_ROOT = Path(__file__).resolve().parents[1]
HIST_PATH = REPO_ROOT / "historial.json"
CHROMA_PATH = REPO_ROOT / "chroma_db"

# Prompt por defecto que define el proposito del asistente
DEFAULT_SYSTEM_PROMPT = (
    "Eres un asistente especializado en la creaci\u00f3n de informes acad\u00e9micos y"
    " corporativos, presentaciones en PowerPoint, hojas de c\u00e1lculo en Excel"
    " y reportes ejecutivos. Tu funci\u00f3n es asistir al usuario en la redacci\u00f3n,"
    " estructuraci\u00f3n y enriquecimiento de contenido profesional, asegurando"
    " claridad, coherencia y pertinencia seg\u00fan el contexto."
)

# Cargar configuración global
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.yaml"
if CONFIG_PATH.exists():
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        CONFIG = yaml.safe_load(fh) or {}
else:
    CONFIG = {}

SYSTEM_PROMPT = CONFIG.get("system_prompt", DEFAULT_SYSTEM_PROMPT)

# Lenguaje por sesión
_LANG_STORE: dict[str, str] = {"default": CONFIG.get("language", "es")}


def get_language(session_id: str = "default") -> str:
    return _LANG_STORE.get(session_id, CONFIG.get("language", "es"))


def set_language(lang_code: str, session_id: str = "default") -> None:
    if lang_code not in {"es", "en"}:
        lang_code = "es"
    _LANG_STORE[session_id] = lang_code

# Instancia global del modelo para reutilizar conexiones
MODEL_NAME = CONFIG.get("model", "mixtral")
llm = OllamaLLM(model=MODEL_NAME) if OllamaLLM else None

def _invoke_llm(prompt: str) -> str:
    """Invoca el modelo compatible con LangChain."""
    if llm is None:
        if shutil.which("ollama"):
            try:
                proc = subprocess.run(
                    ["ollama", "run", MODEL_NAME],
                    input=prompt,
                    text=True,
                    capture_output=True,
                    check=True,
                    encoding="utf-8",
                )
                return proc.stdout
            except Exception as exc:  # pragma: no cover - runtime connectivity issues
                raise HTTPException(status_code=503, detail="LLM no disponible") from exc
        raise HTTPException(status_code=503, detail="LLM no disponible")
    try:
        if hasattr(llm, "invoke"):
            return llm.invoke(prompt)
        return llm(prompt)
    except OllamaEndpointNotFoundError:
        raise
    except Exception as exc:  # pragma: no cover - runtime connectivity issues
        raise HTTPException(status_code=503, detail="LLM no disponible") from exc


def clean_llm_output(text: str) -> str:
    """Normaliza y filtra la respuesta del modelo."""
    if not isinstance(text, str):
        text = str(text)
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u2013", "-").replace("\u2014", "-")

    def _repl(match: re.Match) -> str:
        inner = match.group(1)
        if re.fullmatch(r"[A-Za-z0-9 ,.'\"-]+", inner):
            return ""
        return match.group(0)

    text = re.sub(r"\(([^()]+)\)", _repl, text)
    return text.strip()


def detect_language(text: str) -> str:
    """Devuelve 'en' o 'es' según el idioma detectado."""
    if not detect:
        return "es"
    try:
        lang = detect(text)
    except Exception:
        return "es"
    return "en" if lang.startswith("en") else "es"


def invoke_llm(prompt: str, session_id: str = "default") -> str:
    """Invoca el modelo y limpia la salida respetando el idioma activo."""
    lang = get_language(session_id)
    prefix = "Responde en español:\n" if lang == "es" else "Answer in English:\n"
    contexto = obtener_contexto_semantico(prompt)
    full_prompt = SYSTEM_PROMPT + "\n" + prefix + prompt
    if contexto:
        full_prompt += "\nBasate en el siguiente contexto:\n" + contexto
    raw = _invoke_llm(full_prompt)
    return clean_llm_output(raw)

EXPORT_DIR = Path(CONFIG.get("export_dir", "exports"))
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR = REPO_ROOT / "backend" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR = REPO_ROOT / "backend" / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

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
docs_collection = client.get_or_create_collection("documentos") if client else None


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


def agregar_documento(texto: str) -> None:
    """Almacena un documento en la base vectorial de documentos."""
    if not docs_collection or not embedder:
        return
    doc_id = str(uuid4())
    emb_raw = embedder.encode(texto)
    emb = emb_raw.tolist() if hasattr(emb_raw, "tolist") else emb_raw
    try:
        docs_collection.add(ids=[doc_id], embeddings=[emb], documents=[texto])
    except Exception:
        pass


def obtener_contexto_semantico(texto: str, k: int = 2) -> str:
    """Busca fragmentos relevantes en la base vectorial de documentos."""
    if not docs_collection or not embedder or not texto:
        return ""
    emb_raw = embedder.encode(texto)
    emb = emb_raw.tolist() if hasattr(emb_raw, "tolist") else emb_raw
    try:
        res = docs_collection.query(
            query_embeddings=[emb], n_results=k, include=["documents"]
        )
    except Exception:
        return ""
    docs = res.get("documents", [[]])[0]
    return "\n".join(docs)


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
    estructura: str | None = None


_convs: dict[str, EstadoConversacion] = {}
_conv_lock = Lock()


class Mensaje(BaseModel):
    mensaje: str


class ConversacionRequest(BaseModel):
    mensaje: str
    modo: str | None = None


class IdiomaRequest(BaseModel):
    idioma: str


def _iniciar_conv() -> str:
    return "Hola, soy tu asistente IA. ¿Para qué necesitas este informe?"


_PREGUNTAS_PREDETERMINADAS = {
    1: "¿Sobre qué tema específico trata el informe?",
    2: "¿Qué estilo prefieres (técnico, académico, ejecutivo, etc.)?",
    3: "¿Cuántas páginas deseas? (máximo 30)",
    4: "¿Hay fuentes, restricciones o tono específico que debamos considerar?",
}


def generar_pregunta(paso: int, estado: EstadoConversacion) -> str:
    """Genera la siguiente pregunta de forma dinámica usando el LLM."""
    base = _PREGUNTAS_PREDETERMINADAS.get(paso, "")
    if llm is None:
        return base

    prompt = (
        "Eres un asistente que ayuda a planificar un informe. "
        "Con la información recopilada hasta ahora, formula la siguiente pregunta "
        "de manera concisa en español.\n"
        f"Propósito: {estado.proposito or 'N/A'}. "
        f"Tema: {estado.tema or 'N/A'}. "
        f"Estilo: {estado.estilo or 'N/A'}. "
        f"Páginas: {estado.paginas or 'N/A'}. "
        f"Extras: {estado.extras or 'N/A'}. "
    )
    if paso == 1:
        prompt += "Necesitamos conocer el tema específico del informe."
    elif paso == 2:
        prompt += (
            "Necesitamos saber el estilo preferido (técnico, académico, ejecutivo, etc.)."
        )
    elif paso == 3:
        prompt += "Pregunta por la cantidad de páginas deseadas, máximo 30."
    elif paso == 4:
        prompt += "Pregunta si hay fuentes, restricciones o tono a considerar."
    else:
        return base

    try:
        return invoke_llm(prompt)
    except Exception:
        return base


@app.post("/asistente/{conv_id}")
async def asistente(conv_id: str, msg: Mensaje, request: Request):
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
            return {"reply": generar_pregunta(1, estado)}
        if estado.paso == 1:
            estado.tema = texto
            estado.paso = 2
            return {"reply": generar_pregunta(2, estado)}
        if estado.paso == 2:
            estado.estilo = texto
            estado.paso = 3
            return {"reply": generar_pregunta(3, estado)}
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
            return {"reply": generar_pregunta(4, estado)}
        if estado.paso == 4:
            estado.extras = texto
            estado.estructura = generar_estructura(
                estado.tema or "",
                "Informe",
                proposito=estado.proposito,
                estilo=estado.estilo,
                paginas=estado.paginas,
                extras=estado.extras,
                session_id=request.headers.get("X-Session-Id", "default"),
            )
            estado.paso = 5
            return {
                "reply": estado.estructura
                + "\n¿Te parece bien esta estructura? (sí/no)",
                "estructura": estado.estructura,
            }
        if estado.paso == 5:
            if texto.lower().startswith("s"):
                estado.paso = 6
                return {"reply": "Contexto completado", "contexto": estado.dict()}
            else:
                estado.paso = 4
                return {"reply": "Indica los ajustes que deseas realizar"}

    return {"reply": "Conversación finalizada"}

def generar_estructura(
    tema: str,
    tipo: str,
    proposito: str | None = None,
    estilo: str | None = None,
    paginas: int | None = None,
    extras: str | None = None,
    session_id: str = "default",
) -> str:
    """Genera la estructura del informe."""
    prompt = (
        f"Propón una estructura de informe en español tipo \"{tipo}\" sobre \"{tema}\". "
        f"Propósito: {proposito or 'N/A'}. Estilo: {estilo or 'estándar'}. "
        f"Extensión aproximada: {paginas or '5'} páginas. "
        f"Consideraciones: {extras or 'ninguna'}. "
        "Devuelve solo los títulos de las secciones con una breve descripción de cada una."
    )
    try:
        return invoke_llm(prompt, session_id=session_id)
    except OllamaEndpointNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="Modelo Mixtral no encontrado. Ejecute `ollama pull mixtral`",
        ) from exc


def generar_contenido(
    tema: str,
    tipo: str,
    proposito: str | None = None,
    estilo: str | None = None,
    paginas: int | None = None,
    extras: str | None = None,
    contexto: str | None = None,
    session_id: str = "default",
) -> str:
    """Genera un informe usando LangChain + Ollama."""
    prompt = (
        f"Redacta un informe profesional en espa\u00f1ol tipo \"{tipo}\" sobre el tema: \"{tema}\". "
        f"Prop\u00f3sito: {proposito or 'N/A'}. "
        f"Estilo: {estilo or 'est\u00e1ndar'}. "
        f"Extensi\u00f3n aproximada: {paginas or '5'} p\u00e1ginas. "
        "Incluye introducci\u00f3n, desarrollo argumental y conclusiones. "
        f"Consideraciones adicionales: {extras or 'ninguna'}."
    )
    if contexto:
        prompt += "\nUtiliza la siguiente informaci\u00f3n como referencia:\n" + contexto
    try:
        return invoke_llm(prompt, session_id=session_id)
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


def _leer_documento(path: Path, ext: str) -> str:
    """Extrae texto de un archivo según su extensión."""
    if ext == ".pdf":
        if pdfplumber:
            with pdfplumber.open(path) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        if fitz:
            doc = fitz.open(str(path))
            return "\n".join(page.get_text() for page in doc)
        raise HTTPException(status_code=500, detail="Soporte PDF no disponible")
    if ext == ".docx":
        if not Document:
            raise HTTPException(status_code=500, detail="Soporte DOCX no disponible")
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    if ext == ".txt":
        with path.open("r", encoding="utf-8") as fh:
            return fh.read()
    raise HTTPException(status_code=400, detail="Formato no soportado")



class GenerarRequest(BaseModel):
    tema: str
    tipo: str
    proposito: str | None = None
    estilo: str | None = None
    paginas: int | None = None
    extras: str | None = None
    contexto: str | None = None


class GenerarInformeRequest(BaseModel):
    tema: str
    paginas: int | None = None
    estilo: str | None = None
    idioma: str | None = None
    longitud: str | None = None


class ExportarRequest(BaseModel):
    contenido: str
    formato: str


class GenerarDocxRequest(BaseModel):
    tema: str
    objetivo: str | None = None
    audiencia: str | None = None
    idioma: str | None = None


def generar_docx_tema(
    tema: str,
    objetivo: str | None = None,
    audiencia: str | None = None,
    idioma: str | None = None,
    session_id: str = "default",
) -> str:
    """Genera secciones y construye un DOCX temporal."""

    sec_titles = invoke_llm(
        f"Proporciona un título breve en {idioma or 'español'} para un informe sobre {tema}.",
        session_id=session_id,
    )
    sec_intro = invoke_llm(
        f"Redacta una introducción en {idioma or 'español'} sobre {tema} dirigida a {audiencia or 'público general'}.",
        session_id=session_id,
    )
    sec_dev = invoke_llm(
        f"Desarrolla el tema {tema} en {idioma or 'español'} alcanzando el objetivo {objetivo or 'informativo'}.",
        session_id=session_id,
    )
    sec_conc = invoke_llm(
        f"Concluye el informe sobre {tema} en {idioma or 'español'}.",
        session_id=session_id,
    )

    return crear_docx(
        {
            "titulo": sec_titles,
            "introduccion": sec_intro,
            "desarrollo": sec_dev,
            "conclusion": sec_conc,
        },
        TMP_DIR,
    )


@app.post("/documento")
async def cargar_documento(file: UploadFile = File(...)):
    """Sube un documento y devuelve su texto extraído."""
    ext = Path(file.filename).suffix.lower()
    tmp_path = UPLOAD_DIR / f"{uuid4()}{ext}"
    with tmp_path.open("wb") as fh:
        shutil.copyfileobj(file.file, fh)
    file.file.close()
    try:
        texto = _leer_documento(tmp_path, ext)
    finally:
        try:
            tmp_path.unlink()
        except Exception:
            pass
    texto = unicodedata.normalize("NFC", texto)
    agregar_documento(texto)
    return {"contenido": texto}


@app.post("/generar_informe")
async def generar_informe(req: GenerarInformeRequest):
    """Genera un informe por secciones simulando escritura en tiempo real."""
    texto_base = (
        f"Informe en {req.idioma or 'español'} sobre {req.tema}.\n"
        f"Estilo: {req.estilo or 'estándar'}.\n"
    )

    secciones = [
        "Introducción...\n",
        "Desarrollo del tema...\n",
        "Conclusiones.\n",
    ]

    async def gen():
        yield texto_base
        for sec in secciones:
            for ch in sec:
                yield ch
                await asyncio.sleep(0.02)
        yield "\n" + json.dumps({"finalizado": True})

    return StreamingResponse(gen(), media_type="text/plain; charset=utf-8")

@app.post("/generar")
async def generar(req: GenerarRequest, request: Request):
    """Genera un informe real usando LangChain y Ollama."""
    if not req.tema:
        raise HTTPException(status_code=400, detail="Tema es requerido")

    session_id = request.headers.get("X-Session-Id", "default")
    contenido = generar_contenido(
        req.tema,
        req.tipo,
        proposito=req.proposito,
        estilo=req.estilo,
        paginas=req.paginas,
        extras=req.extras,
        contexto=req.contexto,
        session_id=session_id,
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


@app.post("/generar-docx")
async def generar_docx(
    req: GenerarDocxRequest, request: Request, background_tasks: BackgroundTasks
):
    """Genera un documento DOCX listo para descargar."""
    session_id = request.headers.get("X-Session-Id", "default")

    path = generar_docx_tema(
        req.tema,
        objetivo=req.objetivo,
        audiencia=req.audiencia,
        idioma=req.idioma,
        session_id=session_id,
    )

    headers = {
        "Content-Disposition": "attachment; filename='informe.docx'"
    }
    background_tasks.add_task(os.remove, path)
    return StreamingResponse(
        open(path, "rb"),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
        background=background_tasks,
    )


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


def _should_start(text: str) -> bool:
    t = text.lower()
    if "informe" in t and any(w in t for w in ["generar", "crear", "iniciar", "comenzar"]):
        return True
    return False


def _infer_context(text: str) -> dict:
    ctx: dict[str, object] = {}
    m = re.search(r"(\d+)\s*p[áa]g", text, re.I)
    if m:
        ctx["paginas"] = int(m.group(1))
    if re.search(r"ingl[ée]s", text, re.I):
        ctx["idioma"] = "en"
    elif re.search(r"franc[ée]s", text, re.I):
        ctx["idioma"] = "fr"
    else:
        ctx["idioma"] = "es"
    if re.search(r"t[eé]cnic", text, re.I):
        ctx["estilo"] = "técnico"
    elif re.search(r"acad[eé]mic", text, re.I):
        ctx["estilo"] = "académico"
    elif re.search(r"ejecutiv", text, re.I):
        ctx["estilo"] = "ejecutivo"
    m = re.search(r"sobre ([^.\n]+)", text, re.I)
    if m:
        ctx["tema"] = m.group(1).strip()
    if re.search(r"breve|corto", text, re.I):
        ctx["longitud"] = "breve"
    elif re.search(r"largo|extenso", text, re.I):
        ctx["longitud"] = "largo"
    return ctx


def _detect_word_request(text: str) -> str | None:
    """Extrae el tema si el mensaje solicita un documento Word."""
    t = text.lower()
    if not any(k in t for k in ["word", "docx", "documento", "descargar"]):
        return None
    m = re.search(r"sobre ([^.\n]+)", text, re.I)
    if m:
        return m.group(1).strip()
    return text.strip()


def _detect_lang_command(text: str) -> str | None:
    """Devuelve 'es' o 'en' si el texto indica cambiar de idioma."""
    t = text.lower()
    if re.search(r"(english|ingl\xe9s)" , t) and re.search(r"(cambi|switch|quiero|change)", t):
        return "en"
    if re.search(r"(espa\xf1ol|spanish)", t) and re.search(r"(cambi|switch|quiero|change)", t):
        return "es"
    return None


@app.post("/conversar")
async def conversar(req: ConversacionRequest, request: Request):
    """Procesa mensajes libres usando el modelo de lenguaje."""
    prompt = req.mensaje
    if prompt.startswith("UPDATE:"):
        print("Mensaje recibido:", prompt)
        print("Respuesta generada:", "actualizado")
        return {"respuesta": "actualizado"}

    if req.modo == "generar":
        session_id = request.headers.get("X-Session-Id", "default")
        try:
            texto = generar_contenido(prompt, "Informe", session_id=session_id)
        except Exception:
            texto = f"Generando informe: {prompt}"
        print("Mensaje recibido:", prompt)
        print("Respuesta generada:", texto)
        return {"respuesta": texto}

    session_id = request.headers.get("X-Session-Id", "default")
    tema_docx = _detect_word_request(prompt)
    if tema_docx:
        path = generar_docx_tema(tema_docx, session_id=session_id)
        headers = {"Content-Disposition": "attachment; filename='informe.docx'"}
        background_tasks = BackgroundTasks()
        background_tasks.add_task(os.remove, path)
        return StreamingResponse(
            open(path, "rb"),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers,
            background=background_tasks,
        )

    lang_cmd = _detect_lang_command(prompt)
    if lang_cmd:
        set_language(lang_cmd, session_id)
        texto_resp = (
            "Idioma cambiado a Español"
            if lang_cmd == "es"
            else "Language switched to English"
        )
        return {"respuesta": texto_resp}

    try:
        respuesta = invoke_llm(prompt, session_id=session_id)
        error = None
    except HTTPException as exc:
        respuesta = ""
        error = exc.detail
    print("Mensaje recibido:", prompt)
    print("Respuesta generada:", respuesta)

    start = _should_start(prompt)
    ctx = _infer_context(prompt) if start else None
    payload = {
        "respuesta": respuesta,
        "iniciar_generacion": start,
        "contexto": ctx,
    }
    if error:
        payload["error"] = error
    return payload


@app.post("/config/idioma")
async def cambiar_idioma(req: IdiomaRequest, request: Request):
    """Actualiza el idioma de la sesi\u00f3n."""
    session_id = request.headers.get("X-Session-Id", "default")
    set_language(req.idioma, session_id)
    return {"ok": True, "idioma": get_language(session_id)}


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
