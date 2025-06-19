import re
from typing import Dict

def validar_entrada(data: Dict[str, str], pregunta: str) -> Dict[str, object]:
    """Valida la respuesta del usuario para el asistente.

    Parameters
    ----------
    data: Dict[str, str]
        Diccionario con los campos ``step`` e ``input``.
    pregunta: str
        Pregunta actual que se debe responder.
    Returns
    -------
    Dict[str, object]
        Estructura con ``valid`` y ``feedback`` si aplica.
    """
    step = data.get("step", "")
    texto = data.get("input", "").strip()
    resultado: Dict[str, object] = {"step": step, "valid": True}

    if not texto:
        resultado["valid"] = False
        resultado["feedback"] = pregunta
        return resultado

    tnorm = texto.lower()
    # Patrones de saludos o evasivas
    fuera_ctx = [
        r"^(hola|buenas|buenos dias|buenas tardes|buenos días)$",
        r"^(como estas\??|\xc2\xbfcomo estas\??)$",
        r"^(jaja+|ja ja+|haha+|jeje+|xd+)$",
        r"^(no se|no lo se|ni idea|lo que sea|cualquiera)$",
    ]
    if any(re.match(p, tnorm) for p in fuera_ctx):
        resultado["valid"] = False
        resultado["feedback"] = f"{pregunta}"
        return resultado

    if step == "longitud":
        dig = re.search(r"\d+", texto)
        if not dig:
            resultado["valid"] = False
            resultado["feedback"] = (
                "Por favor, indica un número de páginas entre 1 y 30 para continuar."
            )
            return resultado
        num = int(dig.group())
        if num < 1 or num > 30:
            resultado["valid"] = False
            resultado["feedback"] = (
                "Por favor, indica un número de páginas entre 1 y 30 para continuar."
            )
            return resultado
        resultado["value"] = num
        return resultado

    # Respuestas demasiado cortas o ambiguas
    if len(tnorm) <= 2 or tnorm in {"si", "no", "?"}:
        resultado["valid"] = False
        resultado["feedback"] = f"{pregunta}"
    return resultado

