# agents.md – Documentación de Agentes Lógicos del Sistema

Este documento describe los agentes lógicos internos del sistema **IA Work Generator**, responsables de la orquestación, generación y gestión contextual del contenido. Cada agente cumple una función especializada dentro del flujo de generación, y su modularidad permite extender o sustituir componentes sin afectar la lógica global.

## Agente de Contexto

**Función:** Recopila los parámetros iniciales a través de una conversación estructurada. Define el propósito, tono, nivel de formalidad, audiencia y estructura deseada. Utiliza prompts guía para construir una representación semántica del informe antes de iniciar la generación.

**Entradas:**

* Propósito del informe
* Audiencia objetivo
* Nivel de formalidad
* Tono deseado
* Longitud esperada

**Salidas:**

* Esquema estructural con secciones y subtítulos sugeridos
* Metadatos iniciales del informe
* Estado contextual persistente

## Agente Generador de Texto

**Función:** Ejecuta la generación progresiva de contenido por secciones, utilizando los modelos LLM locales mediante LangChain y Ollama. Cada bloque generado es anotado con un identificador estructurado (ID de sección) para permitir trazabilidad, edición dirigida y análisis semántico posterior.

**Entradas:**

* Sección a generar (ID + título)
* Contexto global del documento
* Plantilla estilística (si aplica)

**Salidas:**

* Texto generado para la sección
* Identificador único del contenido
* Registro en historial

## Agente de Secciones

**Función:** Organiza y mantiene una jerarquía de secciones y subsecciones. Implementa un árbol estructural que vincula títulos, subtítulos y párrafos. Permite operaciones como conteo, localización, edición selectiva o eliminación de componentes individuales del informe.

**Entradas:**

* Árbol de estructura textual
* Solicitudes del usuario (consultas tipo "modifica", "cuenta", "elimina")

**Salidas:**

* Referencia a la sección objetivo
* Métricas asociadas (caracteres, palabras, profundidad)
* Actualización estructural en tiempo real

## Agente Editor

**Función:** Presenta el contenido al usuario con opciones para modificar, regenerar o reescribir cualquier fragmento. Aplica sugerencias del usuario sobre el texto, conservando la coherencia con el contexto general y realizando ajustes estilísticos automáticos si es necesario.

**Entradas:**

* Texto existente
* Instrucciones del usuario (por ej., "hazlo más formal")
* ID de sección

**Salidas:**

* Nueva versión del texto
* Registro de cambios

## Agente Exportador

**Función:** Prepara y exporta el contenido a formatos como DOCX y PDF mediante Pandoc. Valida la integridad estructural del documento antes de su compilación final, incluyendo portada, índice si se requiere, y metadatos.

**Entradas:**

* Documento completo (estructura + contenido)
* Formato deseado
* Opciones de exportación (estilo, plantilla visual)

**Salidas:**

* Archivo final exportado
* Registro en historial

## Agente de Historial Semántico

**Función:** Mantiene un repositorio local de informes previos, accesible mediante búsqueda semántica via ChromaDB. Indexa metadatos y contenido textual con embeddings para permitir recuperación inteligente por tema, fecha o estructura.

**Entradas:**

* Informe generado (texto y metadatos)
* Consulta de usuario

**Salidas:**

* Resultados relevantes por similitud
* Carga de informe anterior en editor

---

Cada agente está diseñado bajo principios de independencia funcional, trazabilidad y extensibilidad. La integración entre agentes se realiza mediante paso de contexto enriquecido (context objects), permitiendo conservar el estado conversacional y estructural del documento en todo momento.
