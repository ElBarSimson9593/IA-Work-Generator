# Documentación de Agentes Lógicos

Este documento describe la lógica interna y los componentes funcionales que orquestan el comportamiento inteligente de **IA Work Generator**. Cada agente actúa como una entidad modular con responsabilidades bien definidas, facilitando el razonamiento contextual, la generación coherente y la adaptabilidad de la aplicación a distintos casos de uso.

## 1. Agente de Contexto

### Rol principal:

Responsable de iniciar la interacción con el usuario y extraer los parámetros fundamentales para la generación del informe. Opera mediante un flujo conversacional guiado.

### Funciones clave:

* Identificación del propósito del informe.
* Definición del tono (formal, técnico, divulgativo, etc.).
* Segmentación del público objetivo.
* Configuración del nivel de profundidad deseado.
* Propuesta de una estructura preliminar del documento.

### Implementación:

Basado en LangChain con prompts estructurados. Utiliza plantillas preconfiguradas según dominio (académico o corporativo) para ajustar el framing inicial.

## 2. Agente Generador de Texto

### Rol principal:

Encargado de la generación progresiva de contenido textual a partir del contexto validado. Secciona el contenido según la estructura acordada.

### Funciones clave:

* Redacción sección por sección (introducción, desarrollo, conclusión, etc.).
* Simulación de escritura en tiempo real.
* Mecanismos de retroalimentación ante ambigüedades.
* Modularidad para regeneración selectiva.

### Implementación:

Utiliza Ollama como backend de inferencia LLM y se orquesta mediante LangChain para mantener coherencia entre secciones. Aplica prompts contextuales enriquecidos con memoria temporal.

## 3. Agente Editor

### Rol principal:

Proporciona un entorno de edición enriquecida donde el usuario puede ajustar, corregir o solicitar regeneraciones parciales del contenido generado.

### Funciones clave:

* Edición directa del contenido.
* Reescritura bajo diferentes estilos o enfoques.
* Regeneración contextual de secciones marcadas.
* Validación semántica y sugerencias de mejora.

### Implementación:

Interfaz React con integración a un backend de microservicios que consulta a LangChain con prompts de revisión. Se apoya en historiales previos y plantillas adaptativas.

## 4. Agente de Exportación

### Rol principal:

Encargado de transformar el contenido final en formatos profesionales editables y de registrar su traza documental.

### Funciones clave:

* Conversión a DOCX y PDF mediante Pandoc.
* Inserción de metadatos (título, autor, fecha, parámetros contextuales).
* Registro automático en historial.
* Preparación para exportaciones futuras (pptx, xlsx).

### Implementación:

Pipeline de renderizado basado en Pandoc con plantillas Markdown enriquecidas. Se apoya en los archivos de `resources/` para asegurar consistencia visual y estructural.

## 5. Agente de Historial y Memoria

### Rol principal:

Gestiona la persistencia de contenidos generados, habilitando la búsqueda semántica, el versionado y la reutilización inteligente de informes.

### Funciones clave:

* Indexación semántica con ChromaDB.
* Búsqueda por intención, título o contexto.
* Agrupación de informes por temática o dominio.
* Versionado y trazabilidad del contenido.

### Implementación:

Integración directa con ChromaDB usando embeddings generados por `sentence-transformers`. Se apoya en `historial.json` como capa de persistencia local.

---

Cada agente está diseñado para operar de forma desacoplada pero interoperable, lo que permite escalar funcionalmente el sistema sin introducir cuellos de botella lógicos. La arquitectura modular garantiza la posibilidad de sustituir, ampliar o especializar agentes sin comprometer la estabilidad del ecosistema general.
