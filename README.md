# IA Work Generator – Generador de Informes con IA Local

**IA Work Generator** es una aplicación de escritorio, completamente local, diseñada para automatizar la redacción de informes extensos en contextos académicos y empresariales. Su arquitectura prioriza la eficiencia operativa y la soberanía de los datos mediante el uso exclusivo de modelos de lenguaje offline, prescindiendo completamente de servicios en la nube. Gracias a su diseño optimizado, es capaz de ejecutarse en hardware modesto, adaptando dinámicamente su comportamiento si detecta una GPU disponible, con el fin de maximizar la velocidad de inferencia y la experiencia de usuario.

## Capacidades estratégicas

El sistema inicia con una interfaz guiada que permite al usuario seleccionar la longitud y nivel de profundidad del informe deseado. Un asistente conversacional estructurado recopila los parámetros clave —propósito del documento, tono, público objetivo y nivel de detalle— mediante un diálogo controlado. Tras la validación del contexto, se inicia una generación progresiva por secciones, con simulación visual de escritura. Este enfoque busca reforzar la percepción de control y transparencia. El usuario puede intervenir mediante un editor interactivo antes de proceder a la exportación final, soportada por Pandoc, en formatos profesionales como DOCX o PDF.

La persistencia del conocimiento generado se garantiza a través de un historial estructurado, con búsqueda semántica optimizada mediante ChromaDB. La plataforma está diseñada para escalar hacia funcionalidades futuras como exportación a presentaciones (.pptx), hojas de cálculo (.xlsx) y cuadros de mando ejecutivos.

## Tecnologías empleadas

La interfaz combina Tauri, React, TailwindCSS y ShadCN UI, con el objetivo de ofrecer una experiencia ligera, nativa y coherente. El backend, por su parte, está construido sobre FastAPI e integra LangChain para la orquestación de flujos LLM, mientras que Ollama se encarga de la ejecución eficiente de los modelos.

## Inteligencia adaptativa

En ausencia de GPU (con al menos 4 GB de RAM), se emplean modelos cuantizados como `mistral` o `mixtral`, permitiendo una generación dividida en secciones para reducir el impacto en recursos. En presencia de GPU compatibles con CUDA o Metal, el sistema activa automáticamente la aceleración por hardware, reduciendo drásticamente los tiempos de respuesta sin comprometer la calidad del texto generado.

## Arquitectura modular

El proyecto se estructura en componentes claramente diferenciados para facilitar el mantenimiento y la extensión:

* `frontend/`: Interfaz de usuario con tecnologías web modernas.
* `backend/`: Núcleo funcional expuesto mediante API REST.
* `resources/`: Plantillas editables para personalización de salida.
* `config/`: Configuraciones generales para comportamiento del sistema.
* `historial.json`: Repositorio local de informes generados.
* `agents.md`: Documentación de los agentes lógicos y flujos.

## Flujo de navegación

La experiencia del usuario se articula en cuatro fases secuenciales, cada una protegida por una lógica de validación que impide avanzar hasta completar la tarea actual. Esto refuerza la coherencia y evita errores por omisión.

1. El **asistente de contexto** inicia el diálogo con el usuario y propone una estructura preliminar que debe ser aprobada explícitamente.
2. Una vez validado el enfoque, comienza la **redacción animada**, donde el contenido se construye en tiempo real por secciones.
3. Finalizada la generación, el usuario accede al **editor interactivo**, con funciones de revisión, regeneración parcial y edición enriquecida.
4. Finalmente, se accede al módulo de **exportación**, donde se selecciona el formato de salida y se registra el informe en el historial.

## Diseño de componentes

Los elementos de la interfaz han sido seleccionados por su accesibilidad y coherencia visual. Se emplean `Stepper`, `Tabs`, `Progress`, `Card`, `Select`, entre otros, asegurando una experiencia fluida desde la definición hasta la exportación del informe. Los elementos del historial permiten inspeccionar, buscar y reutilizar informes anteriores con rapidez.

## Esquemas funcionales

### Flujo de usuario

```text
[Inicio de aplicación]
        ↓
[Asistente de contexto: definición y validación]
        ↓
[Generación animada por secciones]
        ↓
[Editor interactivo: ajustes y confirmación]
        ↓
[Exportación a DOCX/PDF]
        ↓
[Registro en historial con metadatos y búsqueda semántica]
```

### Arquitectura técnica

```text
+----------------------+     REST API     +----------------------+    Exportación     +----------------------+
|  Frontend (Tauri)    | <--------------> |   Backend (FastAPI)   |  ------------->  |  Pandoc / Sistema FS |
| - React UI           |                  | - LangChain + Ollama |                  | - DOCX / PDF         |
| - Navegación guiada  |                  | - ChromaDB / NLP      |                  |                      |
+----------------------+                  +----------------------+                  +----------------------+
```

### Módulos lógicos

```text
[Agente de Contexto] ---> [Generador de Texto] ---> [Editor Interactivo] ---> [Exportador de Documento]
                                ↑                             ↓                           ↓
                      [Motor Semántico (Chroma)] <---- [Historial Persistente]     [Plantillas y Config]
```

## Instrucciones de despliegue

### Backend

Se recomienda iniciar Ollama con el modelo adecuado:

```bash
ollama run mixtral
ollama serve &
```

En caso de error por endpoint:

```bash
ollama pull mixtral
```

Para equipos limitados:

```bash
ollama pull mistral
```

Configurar `config/config.yaml` con `model: mistral` según corresponda. Luego:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -U langchain-community sentence-transformers
```

Instalar Pandoc:

```bash
sudo apt-get install pandoc  # Linux
brew install pandoc          # macOS
```

Ejecutar el backend:

```bash
python backend/main.py
```

### Frontend

En la raíz del frontend:

```bash
cd frontend
npm install
npm run dev
```

La aplicación se abrirá en modo desarrollo con el asistente activo.

## Pruebas y distribución

Ejecución de pruebas automatizadas:

```bash
pytest
```

Compilación del backend:

```bash
sh backend/build.sh
```

Empaquetado de la aplicación final:

```bash
npm run tauri build
```

## Perspectiva de evolución

Se contempla una evolución funcional hacia:

* Personalización completa de plantillas.
* Exportación directa a .pptx y .xlsx.
* Dashboards integrados con Power BI.
* Soporte para múltiples idiomas.
* Adaptación a verticales específicos (ingeniería, medicina, derecho, etc.).
* Backend autónomo y empaquetable sin dependencias externas.

## Licencia

MIT – Libre uso, modificación y distribución, requiriendo atribución correspondiente.
