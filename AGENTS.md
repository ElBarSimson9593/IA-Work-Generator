# Arquitectura de Agentes Inteligentes – IA Work Generator

Este documento describe los agentes que componen la lógica del sistema IA Work Generator. Cada agente cumple una función específica dentro del flujo de generación, edición y exportación de informes, permitiendo una arquitectura modular, extensible y optimizada para entornos locales.

---

## Agente: Asistente Curioso (Conversacional Inicial)

**Propósito:** Recopilar todos los parámetros clave del informe antes de iniciar su generación.

* **Tipo:** Agente de entrada basado en modelo LLM (Ollama).
* **Entrada esperada:** Respuestas del usuario a preguntas progresivas (tema, objetivo, estilo, extensión, público, fuentes).
* **Salida:** Objeto JSON estructurado con los parámetros recopilados.
* **Observación:** Su ejecución es obligatoria antes de habilitar los siguientes pasos.

---

## Agente: Generador de Contenido por Secciones

**Propósito:** Producir un informe completo dividiéndolo en partes (introducción, desarrollo, conclusión) según el contexto aportado.

* **Tipo:** Agente generativo secuencial.
* **Modelo:** Ollama (modelos configurables en `config.yaml`).
* **Entrada:** Contexto estructurado generado por el Asistente Curioso.
* **Comportamiento:**

  * Divide el informe en bloques proporcionales a la cantidad de páginas solicitadas (hasta 30).
  * Emite el texto de forma progresiva con animación en tiempo real.
  * Compatible con CPU y GPU (autoajuste).
  * Soporta "modo ahorro" para bajo consumo.
* **Salida:** Texto markdown enriquecido para edición posterior.

---

## Agente: Editor Interactivo

**Propósito:** Permitir al usuario modificar el contenido generado antes de exportarlo.

* **Tipo:** Agente de interfaz (no LLM).
* **Interfaz:** Editor integrado en la UI con soporte markdown.
* **Controles:**

  * Botones para guardar, regenerar o continuar hacia exportación.
  * Tabs o secciones para visualizar cada parte del informe.
* **Observación:** Paso opcional pero recomendado antes de la exportación final.

---

## Agente: Exportador de Documentos

**Propósito:** Convertir el markdown generado a formatos profesionales.

* **Tipo:** Agente de transformación documental.
* **Tecnología:** Pandoc, llamado desde backend.
* **Entradas:**

  * Texto markdown editado.
  * Plantillas opcionales (`resources/template.docx`, `template.css`).
  * Formato de salida elegido (DOCX o PDF).
* **Salida:** Archivo generado en carpeta definida por `config.yaml`.

---

## Agente: Buscador Semántico

**Propósito:** Recuperar informes anteriores relevantes mediante comparación semántica.

* **Tecnología:** ChromaDB + sentence-transformers.
* **Entrada:** Query textual libre del usuario.
* **Parámetros:** `k` número de resultados más cercanos.
* **Salida:** Lista de informes con resumen, fecha y opción de exportación directa.

---

## Futuro: Orquestador de Agentes

**Objetivo:** Coordinar de forma automática la ejecución secuencial y adaptativa de todos los agentes descritos.

* Validar completitud del contexto antes de generar.
* Determinar estrategias según el rendimiento disponible (modo ahorro, GPU).
* Recomendar secciones a regenerar o expandir.
* Enlazar resultados del historial como fuentes de referencia.

---

Esta arquitectura orientada a agentes permite escalar el sistema hacia funcionalidades avanzadas de productividad, manteniendo simplicidad en el flujo de usuario y eficiencia en ejecución local.
