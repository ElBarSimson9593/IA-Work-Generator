# Arquitectura de Agentes Inteligentes – IA Work Generator

Este documento describe la arquitectura y comportamiento de los agentes inteligentes del sistema. Cada agente está diseñado como un componente modular, autónomo, y orientado a tareas específicas, utilizando modelos de lenguaje local desplegados con Ollama y coordinados mediante lógica de flujo conversacional.

---

## Agente: Asistente Curioso (Preprocesador Conversacional)

**Función:** Inicia una conversación estructurada con el usuario para comprender a fondo el propósito del informe antes de generarlo. Actúa como un recolector de contexto, estilo y requisitos clave.

- **Tipo:** Conversacional, basado en prompts dinámicos.
- **LLM utilizado:** Ollama (modelo configurable vía `config.yaml`: `mistral`, `mixtral`, etc.).
- **Flujo:**  
  - Recoge propósito (“¿Para qué necesitas este informe?”)  
  - Solicita tema específico y enfoque  
  - Pregunta por el estilo (técnico, académico, ejecutivo, etc.)  
  - Solicita número de páginas (máx. 30)  
  - Identifica fuentes deseadas, limitaciones o tono  
- **Resultado:** Construye un objeto de configuración contextual que será utilizado por el generador de contenido.

---

## Agente: Generador de Contenido (Redactor por Secciones)

**Función:** Produce el informe completo, estructurado en partes, a partir del contexto recopilado por el asistente. Permite animación progresiva durante la escritura.

- **Tipo:** Generativo, orientado a estructura por secciones.
- **LLM utilizado:** Ollama
- **Técnica:** Prompt adaptativo por bloque (introducción, desarrollo, conclusión).
- **Modo de operación:**  
  - Divide el objetivo en secciones estimadas por número de páginas  
  - Genera secuencialmente cada parte con control de longitud y estilo  
  - Inserta pausas o throttling si está en modo ahorro  
  - Permite monitoreo y edición en tiempo real desde el frontend  
- **Configuración sensible:**  
  - `modo_ahorro`: Reduce frecuencia de tokens, limita longitud de contexto  
  - `usar_gpu`: Acelera el proceso si se detecta hardware compatible  
  - `formato_objetivo`: markdown enriquecido para exportación posterior  

---

## Agente: Editor Interactivo

**Función:** Permite al usuario visualizar y modificar el contenido generado antes de exportarlo. No genera contenido por sí mismo, pero actúa como una capa de control humano.

- **Tipo:** Interfaz de edición local
- **Interacción:** Panel visual en el frontend (React + Tauri)
- **Modo:**  
  - Vista en tiempo real del texto a medida que se genera  
  - Edición de secciones específicas  
  - Posible integración futura con sugerencias automáticas  
- **Estado actual:** Implementado como editor básico sin corrección automatizada

---

## Agente: Exportador de Documentos

**Función:** Convierte el contenido en Markdown generado a formatos editables o imprimibles (DOCX o PDF).

- **Tecnología:** Pandoc (llamada desde backend)
- **Parámetros de exportación:**  
  - Plantillas (`resources/template.docx`)  
  - Estilos CSS opcionales para PDF  
  - Carpeta de salida definida en `config.yaml`
- **Entrada esperada:** markdown enriquecido y metadatos (autor, título, fecha)
- **Salida:** archivo DOCX o PDF

---

## Agente: Buscador Semántico

**Función:** Recupera informes previos relacionados con una consulta textual utilizando similitud semántica.

- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`
- **Vector store:** ChromaDB
- **Modo de consulta:**  
  - `POST /buscar` con `{"query": "tema", "k": 5}`  
  - Devuelve los informes más similares con resumen, fecha y enlace
- **Estado:** Implementado funcionalmente, pendiente de optimización para grandes volúmenes

---

## Futuro: Orquestador de Agentes

Se prevé desarrollar un sistema de **orquestación** que permita a los agentes trabajar de forma encadenada, adaptativa y jerárquica. Por ejemplo:

- El Asistente Curioso podría delegar al Generador solo ciertas secciones.
- El Buscador Semántico podría ofrecer contenido existente como inspiración o material de referencia.
- El Exportador podría integrarse con plantillas personalizadas por usuario o departamento.

Esta arquitectura orientada a agentes permitirá evolucionar hacia una plataforma de productividad IA más amplia y contextual.

