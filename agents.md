# Documentación de agentes

Este proyecto utiliza agentes de lenguaje para interactuar con el usuario y redactar informes. Se implementan de forma local mediante LangChain y modelos gestionados por Ollama.

## Agente conversacional

El agente conversacional se encarga de recopilar el contexto inicial antes de generar un informe. Realiza preguntas sobre:

- Tema y tipo de documento.
- Estilo y nivel de detalle deseado.
- Objetivo y público al que se dirige.

Las respuestas se utilizan como parte del prompt que finalmente recibe el modelo.

## Agente redactor

Tras reunir la información, el agente redactor produce el contenido de forma secuencial para cada sección del informe. Utiliza la función `generar_contenido` del backend para invocar al modelo configurado en `config/config.yaml`.

Este agente escribe la introducción, desarrollo y conclusiones, respetando el número de páginas solicitado.

## Personalización

Los prompts de ambos agentes pueden ajustarse modificando el código del backend o creando plantillas específicas. También es posible añadir nuevos agentes para tareas como búsqueda de referencias o generación de resúmenes.

