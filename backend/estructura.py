from __future__ import annotations
from dataclasses import dataclass, field
from uuid import uuid4
from typing import Optional, Dict, List, Tuple
import re


@dataclass
class Nodo:
    """Representa un bloque del documento."""

    id: str
    tipo: str  # titulo, subtitulo, parrafo, root
    texto: str
    padre: Optional[str] = None
    hijos: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tipo": self.tipo,
            "texto": self.texto,
            "padre": self.padre,
            "hijos": list(self.hijos),
        }


class DocumentoEstructurado:
    """Documento jer\u00e1rquico compuesto por nodos enlazados."""

    def __init__(self) -> None:
        self.nodos: Dict[str, Nodo] = {}
        self.root_id = self._crear_nodo("root", "Documento", None)

    # ----- Operaciones b\u00e1sicas -----
    def _crear_nodo(self, tipo: str, texto: str, padre: Optional[str]) -> str:
        nid = str(uuid4())
        nodo = Nodo(id=nid, tipo=tipo, texto=texto, padre=padre)
        self.nodos[nid] = nodo
        if padre:
            self.nodos[padre].hijos.append(nid)
        return nid

    def add_section(self, tipo: str, texto: str, padre_id: Optional[str] = None) -> str:
        """Agrega un nodo bajo el padre indicado y devuelve su ID."""
        padre_id = padre_id or self.root_id
        if padre_id not in self.nodos:
            raise ValueError("padre_id no existe")
        return self._crear_nodo(tipo, texto, padre_id)

    def update_text(self, node_id: str, nuevo_texto: str) -> bool:
        """Actualiza el texto de un nodo."""
        if node_id in self.nodos:
            self.nodos[node_id].texto = nuevo_texto
            return True
        return False

    def delete_section(self, node_id: str) -> bool:
        """Elimina un nodo y sus descendientes."""
        if node_id not in self.nodos or node_id == self.root_id:
            return False

        def _eliminar(nid: str) -> None:
            for child in list(self.nodos[nid].hijos):
                _eliminar(child)
            del self.nodos[nid]

        padre = self.nodos[node_id].padre
        if padre and node_id in self.nodos[padre].hijos:
            self.nodos[padre].hijos.remove(node_id)
        _eliminar(node_id)
        return True

    # ----- Consultas -----
    def count_titles(self) -> Tuple[int, int]:
        titulos = sum(1 for n in self.nodos.values() if n.tipo == "titulo")
        subtitulos = sum(1 for n in self.nodos.values() if n.tipo == "subtitulo")
        return titulos, subtitulos

    def get_character_count(self, section_id: str) -> int:
        if section_id not in self.nodos:
            return 0
        total = 0

        def _sumar(nid: str) -> None:
            nonlocal total
            nodo = self.nodos[nid]
            total += len(nodo.texto)
            for child in nodo.hijos:
                _sumar(child)

        _sumar(section_id)
        return total

    def find_section_by_name(self, nombre: str) -> Optional[str]:
        nombre = nombre.lower()
        for nid, nodo in self.nodos.items():
            if nombre in nodo.texto.lower():
                return nid
        return None

    # ----- Serializaci\u00f3n -----
    def to_dict(self) -> dict:
        return {
            "root_id": self.root_id,
            "nodos": {nid: nodo.to_dict() for nid, nodo in self.nodos.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentoEstructurado":
        obj = cls.__new__(cls)
        obj.nodos = {nid: Nodo(**vals) for nid, vals in data.get("nodos", {}).items()}
        obj.root_id = data.get("root_id")
        return obj


# ----- Interpretaci\u00f3n simple de comandos -----

def interpretar_comando(doc: DocumentoEstructurado, texto_usuario: str) -> str:
    t = texto_usuario.lower().strip()
    if "t\u00edtulos" in t and "subt\u00edtulos" in t:
        tit, sub = doc.count_titles()
        return f"Hay {tit} t\u00edtulos y {sub} subt\u00edtulos."

    m = re.search(r"caracteres tiene (.+)", t)
    if m:
        nombre = m.group(1).strip(" ?")
        for art in ("la ", "el "):
            if nombre.startswith(art):
                nombre = nombre[len(art):]
        nid = doc.find_section_by_name(nombre)
        if nid:
            cnt = doc.get_character_count(nid)
            return f"Esa secci\u00f3n tiene {cnt} caracteres."
        return "Secci\u00f3n no encontrada."

    if t.startswith("puedes modificar el texto de"):
        nombre = t.split("de", 1)[1].strip(" ?")
        nid = doc.find_section_by_name(nombre)
        if nid:
            doc.update_text(nid, "")
            return "Texto actualizado."
        return "Secci\u00f3n no encontrada."

    if "elimina el apartado" in t:
        nombre = t.split("el apartado", 1)[1].strip(" .?")
        if nombre.startswith("de "):
            nombre = nombre[3:]
        nid = doc.find_section_by_name(nombre)
        if nid:
            doc.delete_section(nid)
            return f"Apartado {nombre} eliminado."
        return "Secci\u00f3n no encontrada."

    return "Comando no reconocido."
