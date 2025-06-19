# Agentes Lógicos en IA Work Generator

Este documento detalla la arquitectura funcional de los agentes lógicos implementados en **IA Work Generator**, responsables de la orquestación cognitiva, control de flujo y generación de contenido. La aplicación adopta una estructura basada en agentes para separar responsabilidades, mejorar la trazabilidad de decisiones e incrementar la extensibilidad futura del sistema.

## 1. Agente de Contexto (`AsistenteCurioso`)

Este agente es el primer punto de contacto con el usuario. Su rol principal es guiar la definición del encargo textual mediante preguntas sucesivas que permiten construir un "prompt de alto nivel". Internamente se comporta como una máquina de estados, donde cada respuesta del usuario transiciona hacia un nuevo nodo de información requerido. Solo tras la confirmación final, este agente emite un evento `onContextConfirmed`, que habilita la generación textual.

Responsabilidades:

* Obtener y refinar información sobre el objetivo del documento.
* Inferir estilo, tono y profundidad mediante heurísticas y ejemplos.
* Establecer metadatos iniciales para la sesion de generación.

## 2. Agente Generador (`RedactorSecuencial`)

Este agente es responsable de la generación secuencial del contenido, utilizando LangChain y modelos ejecutados a través de Ollama. Opera mediante "bloques lógicos" definidos en un grafo de dependencias, donde cada nodo representa una sección del documento (introducción, desarrollo, conclusión, etc.) y cada arista define prerequisitos conceptuales.

Características clave:

* Lógica modular para secciones.
* Capacidad de reintento ante fallos de generación.
* Adaptación de la generación en función del contexto semántico previamente almacenado.

## 3. Agente de Edición (`EditorInteractivo`)

Este agente permite la manipulación del contenido generado antes de su exportación. No actúa como modelo de lenguaje, sino como orquestador de transformaciones estructurales. Expone funciones como:

* Regeneración selectiva de secciones.
* Aplicación de filtros de estilo.
* Validación sintáctica y gramatical básica mediante reglas predefinidas.

## 4. Agente de Exportación (`FormateadorFinal`)

Este agente traduce el contenido Markdown enriquecido hacia formatos finales como DOCX o PDF, integrando metadatos y plantillas. Está integrado con Pandoc y aplica reglas de formateo específicas por tipo de documento.

Funciones destacadas:

* Inserción automática de portada.
* Inclusión de índice si el documento supera cierto umbral de longitud.
* Aplicación de hojas de estilo CSS para coherencia visual.

## 5. Agente de Memoria (`HistorialPersistente`)

Este agente centraliza la gestión de los informes creados. Utiliza ChromaDB para indexar representaciones semánticas de los contenidos generados y metadatos asociados (fecha, autor, ámbito temático, etc.). Facilita la búsqueda por similitud conceptual y recuperación de sesiones anteriores.

Capacidades:

* Indexación incremental al exportar un informe.
* Búsqueda basada en embeddings.
* Recuperación estructurada del contenido previo.

## Orquestación general

Los agentes se comunican mediante eventos y hooks definidos en el backend, con un bus de mensajes interno que garantiza la secuencialidad, consistencia y trazabilidad. La integración con LangChain permite flexibilidad futura para escalar cada agente con cadenas más complejas, agentes autónomos o integraciones con herramientas externas.

## Perspectiva de extensión

La arquitectura actual permite, sin reestructuraciones, la incorporación de agentes especializados para dominios como educación, medicina o legal, así como la adopción de herramientas de validación formal, control de plagio o análisis de impacto.

Este enfoque modular garantiza la sostenibilidad técnica del sistema y su capacidad de adaptarse a requerimientos futuros sin comprometer su desempeño ni su filosofía de privacidad local.
