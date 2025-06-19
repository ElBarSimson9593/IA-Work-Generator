import backend.validador as val


def test_invalido_longitud():
    data = {"step": "longitud", "input": "alo?"}
    res = val.validar_entrada(data, "Indica el número de páginas")
    assert not res["valid"]
    assert "1 y 30" in res["feedback"]


def test_valido_longitud():
    data = {"step": "longitud", "input": "10"}
    res = val.validar_entrada(data, "Indica el número de páginas")
    assert res["valid"]
    assert res["value"] == 10


def test_fuera_contexto():
    data = {"step": "tema", "input": "hola"}
    res = val.validar_entrada(data, "¿Sobre qué tema trata?")
    assert not res["valid"]
    assert "tema" in res["feedback"].lower()

