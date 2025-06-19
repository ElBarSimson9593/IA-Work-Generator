from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import tempfile
import subprocess
import os
from pydantic import BaseModel
from langchain.llms import Ollama

app = FastAPI(title="Generador de informes IA")

# Instancia global del modelo para reutilizar conexiones
llm = Ollama(model="mixtral")


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
    out_path = md_path.replace(".md", ext)

    try:
        subprocess.run(["pandoc", md_path, "-o", out_path], check=True)
    except subprocess.CalledProcessError as exc:
        os.remove(md_path)
        raise HTTPException(status_code=500, detail="Error al exportar") from exc

    os.remove(md_path)
    return out_path

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
    return {"contenido": contenido}


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
