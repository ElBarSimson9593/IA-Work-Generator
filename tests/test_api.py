import json
from pathlib import Path
import os
import sys
sys.path.insert(0, os.path.abspath("."))
from fastapi.testclient import TestClient
import backend.main as bm
from langchain_community.llms.ollama import OllamaEndpointNotFoundError


def setup_module(module):
    bm.HIST_PATH = Path("tests/tmp_hist.json")
    if bm.HIST_PATH.exists():
        bm.HIST_PATH.unlink()
    bm.EXPORT_DIR = Path("tests/exports")
    bm.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    bm.TMP_DIR = Path("tests/tmp")
    bm.TMP_DIR.mkdir(parents=True, exist_ok=True)


client = TestClient(bm.app)


def test_asistente_flujo(monkeypatch):
    monkeypatch.setattr(bm, "generar_estructura", lambda *a, **k: "estructura")
    monkeypatch.setattr(
        bm,
        "generar_pregunta",
        lambda paso, est: bm._PREGUNTAS_PREDETERMINADAS.get(paso, ""),
    )
    cid = "test_conv"
    resp = client.post(f"/asistente/{cid}", json={"mensaje": "hola"})
    assert resp.status_code == 200
    assert "Para qué" in resp.json()["reply"]

    resp = client.post(f"/asistente/{cid}", json={"mensaje": "Trabajo"})
    assert "tema" in resp.json()["reply"].lower()

    resp = client.post(f"/asistente/{cid}", json={"mensaje": "IA"})
    assert "estilo" in resp.json()["reply"].lower()

    resp = client.post(f"/asistente/{cid}", json={"mensaje": "tecnico"})
    assert "páginas" in resp.json()["reply"].lower() or "paginas" in resp.json()["reply"].lower()

    resp = client.post(f"/asistente/{cid}", json={"mensaje": "5"})
    assert "fuentes" in resp.json()["reply"].lower()

    resp = client.post(f"/asistente/{cid}", json={"mensaje": "ninguna"})
    assert "estructura" in resp.json()["reply"].lower()

    resp = client.post(f"/asistente/{cid}", json={"mensaje": "sí"})
    data = resp.json()
    assert data["reply"] == "Contexto completado"
    assert data["contexto"]["paginas"] == 5


def test_generar(monkeypatch):
    monkeypatch.setattr(bm, "generar_contenido", lambda *a, **k: "contenido")
    resp = client.post("/generar", json={"tema": "x", "tipo": "y"})
    assert resp.status_code == 200
    data = resp.json()
    assert "contenido" in data


def test_generar_sin_llm(monkeypatch):
    monkeypatch.setattr(bm, "llm", None)
    monkeypatch.setattr(bm.shutil, "which", lambda x: None)
    resp = client.post("/generar", json={"tema": "x", "tipo": "y"})
    assert resp.status_code == 503
    assert resp.json()["detail"] == "LLM no disponible"


def test_generar_modelo_no_encontrado(monkeypatch):
    def _fail(prompt):
        raise OllamaEndpointNotFoundError("not found")

    monkeypatch.setattr(bm, "llm", _fail)
    resp = client.post("/generar", json={"tema": "x", "tipo": "y"})
    assert resp.status_code == 500
    assert "pull mixtral" in resp.json()["detail"]


def test_exportar(monkeypatch, tmp_path):
    file = tmp_path / "tmp.docx"
    monkeypatch.setattr(bm, "exportar_a_archivo", lambda c, f: str(file))
    resp = client.post("/exportar", json={"contenido": "c", "formato": "docx"})
    assert resp.status_code == 200


def test_buscar(monkeypatch):
    item = {
        "id": "1",
        "tema": "t",
        "tipo": "r",
        "contenido": "algo",
        "timestamp": "2024",
    }
    bm.guardar_historial([item])

    class DummyCol:
        def query(self, query_embeddings, n_results, include):
            return {
                "ids": [["1"]],
                "metadatas": [[{"tema": "t", "tipo": "r", "timestamp": "2024"}]],
            }

    monkeypatch.setattr(bm, "collection", DummyCol())
    monkeypatch.setattr(bm.embedder, "encode", lambda x: [0.0])

    resp = client.post("/buscar", json={"query": "algo"})
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["id"] == "1"


def test_conversar_iniciar():
    """Ensure conversar endpoint triggers generation flag."""
    resp = client.post(
        "/conversar",
        json={"mensaje": "Quiero generar un informe sobre IA"},
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["iniciar_generacion"] is True
    assert "error" in payload


def test_conversar_sin_llm(monkeypatch):
    monkeypatch.setattr(bm, "llm", None)
    monkeypatch.setattr(bm.shutil, "which", lambda x: None)
    resp = client.post("/conversar", json={"mensaje": "hola"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"] == "LLM no disponible"


def test_documento_txt(tmp_path):
    file = tmp_path / "prueba.txt"
    file.write_text("hola", encoding="utf-8")
    with file.open("rb") as fh:
        resp = client.post("/documento", files={"file": ("prueba.txt", fh, "text/plain")})
    assert resp.status_code == 200
    assert resp.json()["contenido"] == "hola"


def test_documento_invalido(tmp_path):
    file = tmp_path / "bad.bin"
    file.write_bytes(b"123")
    with file.open("rb") as fh:
        resp = client.post("/documento", files={"file": ("bad.bin", fh, "application/octet-stream")})
    assert resp.status_code == 400


def test_generar_docx(monkeypatch):
    def fake_llm(prompt, session_id="default"):
        if "título" in prompt.lower():
            return "Titulo de prueba"
        if "introducción" in prompt.lower():
            return "Contenido intro"
        if "desarrolla" in prompt.lower():
            return "Contenido desarrollo"
        if "concluye" in prompt.lower():
            return "Conclusión breve"
        return "texto"

    monkeypatch.setattr(bm, "invoke_llm", fake_llm)
    resp = client.post("/generar-docx", json={"tema": "IA"})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def test_conversar_generar_word(monkeypatch):
    def fake_llm(prompt, session_id="default"):
        if "título" in prompt.lower():
            return "Titulo"
        if "introducción" in prompt.lower():
            return "Intro"
        if "desarrolla" in prompt.lower():
            return "Desarrollo"
        if "concluye" in prompt.lower():
            return "Conclusión"
        return "ok"

    monkeypatch.setattr(bm, "invoke_llm", fake_llm)
    resp = client.post("/conversar", json={"mensaje": "Genera un Word sobre IA"})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def test_cambiar_idioma():
    resp = client.post("/config/idioma", json={"idioma": "en"})
    assert resp.status_code == 200
    assert resp.json()["idioma"] == "en"


def test_conversar_cambia_idioma(monkeypatch):
    monkeypatch.setattr(bm, "_invoke_llm", lambda p: p)
    resp = client.post("/conversar", json={"mensaje": "cambia el idioma a ingles"})
    assert resp.status_code == 200
    assert "Ingl" in resp.json()["respuesta"] or "English" in resp.json()["respuesta"]
    resp2 = client.post("/conversar", json={"mensaje": "hola"})
    assert resp2.status_code == 200
    assert "Answer in English:" in resp2.json()["respuesta"]


def test_rag_document(monkeypatch, tmp_path):
    monkeypatch.setattr(bm, "_invoke_llm", lambda p: p)
    file = tmp_path / "rag.txt"
    file.write_text("dato curioso", encoding="utf-8")
    with file.open("rb") as fh:
        client.post("/documento", files={"file": ("rag.txt", fh, "text/plain")})
    resp = client.post("/conversar", json={"mensaje": "dato curioso"})
    assert resp.status_code == 200
    assert "dato curioso" in resp.json()["respuesta"]
