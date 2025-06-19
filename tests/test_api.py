import json
from pathlib import Path
import os
import sys
sys.path.insert(0, os.path.abspath("."))
from fastapi.testclient import TestClient
import backend.main as bm


def setup_module(module):
    bm.HIST_PATH = Path("tests/tmp_hist.json")
    if bm.HIST_PATH.exists():
        bm.HIST_PATH.unlink()
    bm.EXPORT_DIR = Path("tests/exports")
    bm.EXPORT_DIR.mkdir(parents=True, exist_ok=True)


client = TestClient(bm.app)


def test_generar(monkeypatch):
    monkeypatch.setattr(bm, "generar_contenido", lambda t, ty: "contenido")
    resp = client.post("/generar", json={"tema": "x", "tipo": "y"})
    assert resp.status_code == 200
    data = resp.json()
    assert "contenido" in data


def test_generar_sin_llm(monkeypatch):
    monkeypatch.setattr(bm, "llm", None)
    resp = client.post("/generar", json={"tema": "x", "tipo": "y"})
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Modelo Ollama no disponible"


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
