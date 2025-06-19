# IA Work Generator

Proyecto de ejemplo para generar informes de forma local utilizando un stack libre.

## Estructura

- `frontend/` – Aplicación de escritorio creada con Tauri + React + TailwindCSS + ShadCN UI.
- `backend/` – API local en Python usando FastAPI con LangChain y Ollama.
- `resources/` – Plantillas para exportación (`template.docx`, `template.css`).
- `config/` – Parámetros globales en `config.yaml`.

## Ejecución

### Backend

1. Iniciar Ollama (solo la primera vez es necesario descargar el modelo):

```bash
ollama run mixtral  # descarga el modelo si es necesario
ollama serve &      # deja el servicio escuchando en 11434
```
Si obtienes un error `OllamaEndpointNotFoundError` indicando que el modelo no
existe, ejecuta:

```bash
ollama pull mixtral
```
para descargarlo manualmente.

Para usar un modelo más pequeño puedes ejecutar:

```bash
ollama pull mistral
```
Y establecer `model: mistral` en `config/config.yaml`.

2. Crear entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias (se ha añadido `httpx` para realizar peticiones HTTP):

```bash
pip install -r backend/requirements.txt
pip install -U langchain-community sentence-transformers
```

4. Instalar Pandoc (si no est\u00e1 en el sistema). En Debian/Ubuntu puedes ejecutar:

```bash
sudo apt-get install pandoc
```
En macOS con Homebrew:

```bash
brew install pandoc
```

5. Ejecutar el servidor:

```bash
python backend/main.py
```

La API quedará disponible en `http://127.0.0.1:8000`.
El backend incluye CORS habilitado para las URLs `http://127.0.0.1:1420` y `http://localhost:1420` del frontend.

La configuración global se encuentra en `config/config.yaml` y permite definir
la carpeta de exportación, plantillas y el modelo de Ollama a utilizar.

### Frontend (Tauri)

1. Instalar dependencias de Node:

```bash
cd frontend
npm install
```

2. Ejecutar la aplicación en modo desarrollo:

```bash
npm run dev
```

Tauri abrirá una ventana con el formulario para generar informes.

### Pruebas

Ejecuta las pruebas unitarias con:

```bash
pytest
```

### Empaquetado

Para generar un ejecutable del backend se proporciona `backend/build.sh` que usa
PyInstaller:

```bash
sh backend/build.sh
```

## Flujo básico

1. Introducir un tema y tipo de informe en el formulario.
2. El frontend realiza una petición `POST` a `http://127.0.0.1:8000/generar`.
3. El backend genera el informe usando LangChain + Ollama (modelo Mixtral).
4. El texto se muestra en la interfaz y puede alternarse entre vista con formato (Markdown) o texto plano.
5. Para exportar el informe se hace una petición `POST` a `/exportar` enviando el
   contenido y el formato deseado (`docx` o `pdf`).
6. Los informes se almacenan en `backend/historial.json`. Puede consultarse la
   lista en `GET /historial`, obtener un informe con `GET /historial/{id}` y
   eliminarlo con `DELETE /historial/{id}`. Para exportar un informe guardado se
   puede usar `GET /historial/{id}?exportar=docx` o `pdf`.
7. Para buscar de forma semántica se usa `POST /buscar` con `{ "query": "texto", "k": 5 }` y se obtienen los informes más similares.

Este proyecto está preparado para ampliarse con:

- Almacenamiento y búsqueda semántica con ChromaDB.
- Exportación a DOCX o PDF mediante Pandoc.
- Empaquetado de la aplicación con PyInstaller.
