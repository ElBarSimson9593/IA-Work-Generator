# Arquitectura de Agentes Inteligentes – IA Work Generator

Este documento describe los agentes que componen la lógica interna del sistema IA Work Generator. Cada agente está diseñado con una responsabilidad específica dentro del flujo de generación, edición y exportación de informes. Su arquitectura modular permite escalabilidad, mantenimiento y futura orquestación automatizada.

---

## Agente: Asistente Conversacional Curioso

**Función principal:** Recopilar contexto inicial y objetivos del informe a través de una conversación dirigida.

* **Tipo:** Agente de entrada contextual.
* **Modelo:** Ollama (modelo configurable desde `config.yaml`, como `mistral`, `mixtral`).
* **Lógica:** Prompt orientado a exploración progresiva (tema, público, estilo, cantidad de páginas).
* **Output:** Objeto de configuración estructurado que alimenta al generador.
* **Notas:** Es obligatorio completar esta fase antes de iniciar la redacción.

---

## Agente: Generador de Contenido por Secciones

**Función principal:** Redactar el informe completo, estructurado en bloques (introducción, desarrollo, conclusión), basado en el contexto inicial.

* **Tipo:** Agente generativo secuencial.
* **Modelo:** Ollama, ejecutado localmente.
* **Estrategia:** División por límites de longitud según el número de páginas solicitadas.
* **Capacidades:**

  * Compatibilidad con CPU y GPU.
  * Modo "ahorro" para reducir carga en hardware limitado.
  * Escritura animada visible en tiempo real.
* **Output:** Markdown enriquecido editable.

---

## Agente: Editor Interactivo

**Función principal:** Facilitar la edición manual del texto generado antes de exportarlo.

* **Tipo:** Agente visual sin modelo de lenguaje.
* **Interfaz:** Panel de edición en el frontend (React + ShadCN).
* **Operación:**

  * Edición en tiempo real del contenido generado.
  * Integración futura con sugerencias automáticas y corrección.

---

## Agente: Exportador de Documentos

**Función principal:** Transformar el contenido en Markdown a formatos formales.

* **Tecnología:** Pandoc (invocado desde backend Python).
* **Formatos soportados:** DOCX, PDF.
* **Entrada:** Markdown, metadatos y plantilla opcional (`template.docx`).
* **Configuración:** Controlable desde `config.yaml`.

---

## Agente: Buscador Semántico

**Función principal:** Localizar informes anteriores relevantes usando búsqueda por significado.

* **Tecnología:** `sentence-transformers` + ChromaDB.
* **Consulta:** Texto libre con top-k resultados (`POST /buscar`).
* **Estado:** Implementado y funcional. Admite ampliación con resúcos generados.

---

## Futuro: Orquestador de Agentes

Se prevé desarrollar un orquestador que supervise el flujo completo:

1. Validación del contexto conversacional.
2. Delegación inteligente al generador por bloques.
3. Enriquecimiento desde historial semántico.
4. Propuestas de edición automática.
5. Selección adaptativa de plantilla de exportación.

Esto permitirá una generación de documentos completamente dirigida por IA, con control humano opcional, orientada a escenarios académicos o corporativos profesionales.
