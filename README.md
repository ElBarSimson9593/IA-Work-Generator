# IA Work Generator – Generador de Informes con IA Local

**IA Work Generator** es una aplicación de escritorio de carácter totalmente local, concebida para automatizar la redacción de informes extensos tanto en entornos académicos como empresariales. Su arquitectura pone el foco en la eficiencia operativa y la soberanía de los datos, empleando exclusivamente modelos de lenguaje offline y eliminando por completo la dependencia de servicios en la nube. Gracias a su diseño optimizado, es capaz de ejecutarse en hardware modesto, adaptándose de forma dinámica a la disponibilidad de GPU para maximizar la velocidad de inferencia y mejorar la experiencia de usuario sin comprometer la calidad textual.

## Capacidades estratégicas

El sistema se inicia mediante una interfaz guiada que permite al usuario definir la longitud y el nivel de profundidad del informe. Un asistente conversacional estructurado recoge parámetros clave como el propósito del documento, tono deseado, público objetivo y nivel de formalidad, todo ello mediante un diálogo controlado. Tras la validación del contexto, el sistema procede a una generación progresiva por secciones, acompañada de una simulación visual tipo "escritura en tiempo real", diseñada para reforzar la percepción de control, trazabilidad y transparencia. El usuario puede intervenir en cualquier etapa a través de un editor interactivo enriquecido antes de proceder a la exportación final, soportada por Pandoc, en formatos profesionales como DOCX o PDF.

La persistencia del conocimiento generado se garantiza mediante un historial estructurado, con capacidades de búsqueda semántica optimizadas a través de ChromaDB. El diseño modular de la plataforma facilita su evolución hacia funcionalidades ampliadas como la exportación a presentaciones (.pptx), hojas de cálculo (.xlsx) y cuadros de mando ejecutivos.

## Tecnologías empleadas

La interfaz combina Tauri, React, TailwindCSS y ShadCN UI para ofrecer una experiencia ligera, coherente y visualmente moderna. El backend está construido sobre FastAPI y se apoya en LangChain para la orquestación de flujos con modelos de lenguaje. Ollama se encarga de la ejecución eficiente de modelos LLM locales, mientras que ChromaDB sustenta la indexación semántica.

## Inteligencia adaptativa

En entornos sin GPU, el sistema emplea modelos cuantizados como Mistral o Mixtral, optimizando la generación en bloques para reducir la carga sobre recursos limitados. Cuando se detecta una GPU compatible (CUDA en Linux/Windows o Metal en macOS), se activa automáticamente la aceleración por hardware, mejorando sustancialmente los tiempos de inferencia sin afectar la coherencia narrativa.

## Arquitectura modular

El proyecto se estructura en componentes bien definidos que facilitan su mantenimiento, extensión y depuración:

* **frontend/**: Interfaz de usuario construida con tecnologías web modernas.
* **backend/**: Lógica central expuesta como API REST.
* **resources/**: Plantillas editables para la personalización del contenido generado.
* **config/**: Archivos de configuración del sistema.
* **historial.json**: Repositorio local de informes con metadatos.
* **agents.md**: Documentación interna de los agentes lógicos y sus flujos.

## Flujo de navegación

La experiencia del usuario se estructura en cuatro etapas secuenciales, cada una sujeta a validaciones para garantizar coherencia y evitar omisiones:

1. **Asistente de contexto**: Recoge información clave y propone una estructura inicial, la cual debe ser validada por el usuario.
2. **Redacción animada**: El contenido se genera de forma progresiva por secciones, en un entorno visual que simula la escritura en tiempo real.
3. **Editor interactivo**: Permite revisar, editar o regenerar secciones antes de confirmar la versión final.
4. **Exportación y registro**: Se selecciona el formato deseado y se guarda el informe con metadatos para futuras consultas.

## Diseño de componentes

Los elementos de interfaz se seleccionaron por su accesibilidad y coherencia visual. Se emplean componentes como Stepper, Tabs, Progress, Card y Select, optimizados para una navegación fluida desde la definición inicial hasta la exportación final. El historial permite visualizar, buscar y reutilizar informes anteriores de forma eficiente.

## Esquemas funcionales

### Flujo de usuario

\[Inicio de aplicación] ↓ \[Asistente de contexto: definición y validación] ↓ \[Generación animada por secciones] ↓ \[Editor interactivo: ajustes y confirmación] ↓ \[Exportación a DOCX/PDF] ↓ \[Registro en historial con metadatos y búsqueda semántica]

### Arquitectura técnica

+----------------------+     REST API     +----------------------+    Exportación     +----------------------+
\|  Frontend (Tauri)    | <--------------> |   Backend (FastAPI)   |  ------------->  |  Pandoc / Sistema FS |
\| - React UI           |                  | - LangChain + Ollama |                  | - DOCX / PDF         |
\| - Navegación guiada  |                  | - ChromaDB / NLP      |                  |                      |
+----------------------+                  +----------------------+                  +----------------------+

### Módulos lógicos

\[Agente de Contexto] → \[Generador de Texto] → \[Editor Interactivo] → \[Exportador de Documento]
↑                             ↓                           ↓
\[Motor Semántico (Chroma)] ← \[Historial Persistente]     \[Plantillas y Configuración]

## Instrucciones de despliegue

### Backend

Iniciar Ollama con el modelo adecuado:

```bash
ollama run mixtral
ollama serve &
```

En caso de error por endpoint:

```bash
ollama pull mixtral
```

Para equipos con recursos limitados:

```bash
ollama pull mistral
```

Modificar `config/config.yaml` para usar `model: mistral` si aplica. Luego:

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

En la carpeta raíz del frontend:

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

Se contempla una evolución funcional hacia la personalización integral de plantillas, exportación directa a .pptx y .xlsx, integración con Power BI para dashboards, soporte multilingüe y adaptación a verticales sectoriales como ingeniería, medicina o derecho. Asimismo, se proyecta un backend totalmente autónomo y empaquetable, sin dependencias externas.

## Licencia

MIT – Uso, modificación y distribución libres, con obligatoria atribución al autor original.
