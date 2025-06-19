# IA Work Generator – Generador de Informes con IA Local

**IA Work Generator** es una aplicación de escritorio profesional, completamente local, diseñada para generar informes académicos o corporativos extensos, con modelos de lenguaje ejecutados offline. Opera con bajo consumo de recursos, siendo ideal incluso para PCs de gama baja, y puede escalar su rendimiento al detectar una GPU disponible. El sistema permite generar documentos bien estructurados de hasta 30 páginas, con enfoque personalizado y edición previa a la exportación.

## Características principales

* Generación de informes de hasta 30 páginas mediante IA local (sin conexión a internet).
* El usuario selecciona el número de páginas deseado desde la interfaz.
* Asistente conversacional previo que recopila contexto e intención del informe.
* IA curiosa que hace preguntas profundas: estilo, objetivo, extensión, público, etc.
* Redacción visible en tiempo real con animación de escritura progresiva.
* Edición directa del contenido generado desde un panel interactivo antes de exportar.
* Exportación profesional a DOCX y PDF usando Pandoc.
* Historial persistente y búsqueda semántica con ChromaDB.
* Estructura modular preparada para exportación futura a .pptx, .xlsx, Power BI.
* Interfaz moderna basada en Tauri + React + TailwindCSS + ShadCN UI.

---

## Optimización para distintos entornos

IA Work Generator está diseñado para adaptarse automáticamente a las capacidades del equipo:

**En PCs de gama baja (≥ 4 GB de RAM, sin GPU):**

* Uso de modelos cuantizados (como `mistral`, `mixtral`) mediante Ollama.
* Generación secuencial y por secciones, evitando picos de carga.
* Opción de "modo ahorro": proceso más lento, pero con bajo consumo de CPU y RAM.

**En equipos con GPU disponible:**

* El sistema puede aprovechar la aceleración por hardware (si Ollama está configurado con soporte CUDA/Metal).
* Esto permite una generación significativamente más rápida, útil para documentos largos o múltiples informes en serie.

---

## Estructura del proyecto

* `frontend/` – Aplicación de escritorio: Tauri + React + TailwindCSS + ShadCN UI.
* `backend/` – API en Python: FastAPI + LangChain + Ollama.
* `resources/` – Plantillas para exportación (`template.docx`, `template.css`).
* `config/` – Parámetros globales (`config.yaml`) para modelo, carpeta y estilo.
* `historial.json` – Almacén de informes generados.
* `agents.md` – Documentación técnica de los agentes inteligentes.

---

## Interfaz y navegación

La aplicación está dividida en cuatro vistas principales, conectadas secuencialmente:

1. **Asistente de contexto** – Vista de chat (componente conversacional con flujo tipo wizard). Botón: "Confirmar parámetros".
2. **Redacción del informe** – Vista de generación animada en tiempo real, por secciones. Botón: "Ir al editor".
3. **Editor del informe** – Panel de edición del contenido markdown generado. Botones: "Guardar", "Regenerar", "Ir a exportar".
4. **Exportación** – Selector de formato y botón "Exportar informe".

El usuario solo puede avanzar de una etapa a otra tras completar la actual. Los botones de avance están deshabilitados hasta cumplir condiciones mínimas (ej. contexto válido o generación terminada).

## Componentes UI clave

| Función              | Componente sugerido (ShadCN)       |
| -------------------- | ---------------------------------- |
| Entrada de chat      | `Textarea`, `Button`               |
| Flujo conversacional | `Stepper`, `Form`, validación UX   |
| Vista de generación  | `Progress`, `Card`, `Badge`        |
| Editor de texto      | `Textarea`, `Tabs`, `Toolbar`      |
| Exportar informe     | `Select`, `Button`, `AlertDialog`  |
| Historial            | `Table`, `SearchInput`, `Dropdown` |

---

## Diagramas funcionales

### Diagrama de flujo de interacción

```text
[Inicio de la aplicación]
        ↓
[Chat con IA curiosa]
  (recopila tema, objetivo, estilo, número de páginas)
        ↓
[Confirmación de parámetros por el usuario]
        ↓
[Generación progresiva del informe]
  (secciones: introducción, desarrollo, conclusión)
        ↓
[Vista en tiempo real + Edición manual]
        ↓
[Exportación a DOCX o PDF]
        ↓
[Almacenamiento en historial + Búsqueda semántica opcional]
```

### Diagrama de componentes del sistema

```text
+----------------------+     REST API     +----------------------+    File Export   +----------------------+
|  Frontend (Tauri)    | <--------------> |   Backend (FastAPI)   |  ------------->  |  Pandoc / FileSystem |
| - React UI           |                  | - LangChain + Ollama |                  | - DOCX / PDF         |
| - Chat & Editor      |                  | - ChromaDB, NLP       |                  |                      |
+----------------------+                  +----------------------+                  +----------------------+
```

### Diagrama de agentes

```text
[Asistente Curioso] ---> [Generador de Contenido] ---> [Editor Interactivo] ---> [Exportador de Documentos]
                                ↑                             ↓                           ↓
                        [Buscador Semántico]  <----------  [Historial]               [Plantillas / Config]
```

Estos diagramas resumen cómo fluyen los datos y cómo se estructuran los módulos internos y agentes.

---

## Ejecución

### Backend

1. Iniciar Ollama y el modelo (por primera vez):

```bash
ollama run mixtral
ollama serve &
```

> Si aparece `OllamaEndpointNotFoundError`, ejecuta:

```bash
ollama pull mixtral
```

> Para un entorno más ligero:

```bash
ollama pull mistral
```

Y modifica `config/config.yaml` con `model: mistral`.

2. Crear entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:

```bash
pip install -r backend/requirements.txt
pip install -U langchain-community sentence-transformers
```

4. Instalar Pandoc (si no está en el sistema):

```bash
# Debian/Ubuntu
sudo apt-get install pandoc

# macOS
brew install pandoc
```

5. Ejecutar el servidor:

```bash
python backend/main.py
```

El backend se expone en: `http://127.0.0.1:8000`.

CORS habilitado para: `http://127.0.0.1:1420` y `http://localhost:1420`.

---

### Frontend (Tauri)

1. Instalar dependencias:

```bash
cd frontend
npm install
```

2. Ejecutar la aplicación:

```bash
npm run dev
```

Se abrirá una ventana con el chat del bot y el generador de informes.

---

## Flujo de uso

1. Inicia conversación con la IA, que hará preguntas clave sobre el informe.
2. Selecciona el número de páginas deseado (hasta 30).
3. Visualiza la redacción animada en tiempo real por secciones.
4. Edita el texto generado en el panel antes de exportarlo.
5. Exporta el contenido como DOCX o PDF.
6. Consulta el historial o realiza búsquedas semánticas para reutilizar trabajos anteriores.

---

## Pruebas

Puedes ejecutar pruebas automatizadas con:

```bash
pytest
```

---

## Empaquetado

Para compilar el backend como ejecutable:

```bash
sh backend/build.sh
```

> Integra PyInstaller y empaqueta con todas las dependencias necesarias.

Para empaquetar el frontend con Tauri:

```bash
npm run tauri build
```

---

## Roadmap

* Plantillas exportables configurables por usuario
* Generación de presentaciones PowerPoint (.pptx)
* Exportación estructurada a Excel (.xlsx)
* Dashboards ejecutivos en Power BI / CSV
* Soporte multilenguaje y ajustes de estilo por disciplina
* Compresión del backend y runtime unificado sin dependencias externas

---

## Licencia

MIT – Libre uso, modificación y distribución con atribución.
