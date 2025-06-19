import backend.estructura as es


def _crear_documento():
    doc = es.DocumentoEstructurado()
    intro = doc.add_section("titulo", "Introduccion")
    metodo = doc.add_section("subtitulo", "Metodologia", intro)
    doc.add_section("parrafo", "Texto de prueba", metodo)
    return doc, intro, metodo


def test_operaciones_basicas():
    doc, intro, metodo = _crear_documento()
    tit, sub = doc.count_titles()
    assert tit == 1 and sub == 1
    assert doc.find_section_by_name("Metodologia") == metodo
    doc.update_text(metodo, "Nueva metodologia")
    assert doc.get_character_count(metodo) >= len("Nueva metodologia")
    doc.delete_section(metodo)
    assert doc.find_section_by_name("Metodologia") is None


def test_serializacion():
    doc, intro, _ = _crear_documento()
    data = doc.to_dict()
    nuevo = es.DocumentoEstructurado.from_dict(data)
    assert nuevo.find_section_by_name("Introduccion") == intro


def test_interpretar_comando():
    doc, intro, metodo = _crear_documento()
    resp = es.interpretar_comando(doc, "¿Cuántos títulos y subtítulos tengo?")
    assert "1" in resp
    resp2 = es.interpretar_comando(doc, "¿Cuántos caracteres tiene la Metodologia?")
    assert "caracteres" in resp2
    es.interpretar_comando(doc, "Elimina el apartado de Metodologia.")
    assert doc.find_section_by_name("Metodologia") is None
