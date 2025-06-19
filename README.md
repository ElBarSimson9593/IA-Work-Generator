# IA Work Generator – Generador de Informes con IA Local

**IA Work Generator** es una aplicación de escritorio de carácter local, concebida para automatizar la redacción de informes extensos tanto en entornos académicos como empresariales. Su arquitectura está orientada a la eficiencia operativa y la soberanía de los datos, empleando exclusivamente modelos de lenguaje offline, lo que elimina la dependencia de servicios en la nube. Su diseño está optimizado para ejecutarse en hardware modesto, adaptándose dinámicamente a la disponibilidad de GPU para maximizar la velocidad de inferencia sin comprometer la calidad textual.

## Capacidades Estratégicas

El sistema se inicia con una interfaz guiada que permite definir la extensión y profundidad del informe. Un asistente conversacional recoge parámetros clave como el propósito del documento, tono, público objetivo y nivel de formalidad mediante un diálogo controlado. Una vez validado el contexto, la generación se realiza por secciones, simulando visualmente una "escritura en tiempo real" que refuerza la sensación de trazabilidad y control. El usuario puede intervenir en cualquier etapa mediante un editor interactivo enriquecido antes de exportar en formatos profesionales como DOCX o PDF, soportado por Pandoc.

El conocimiento generado se almacena en un historial estructurado, con búsqueda semántica optimizada a través de ChromaDB. La arquitectura modular permite escalar el sistema a nuevas funcionalidades como exportación a presentaciones (.pptx), hojas de cálculo (.xlsx) o cuadros de mando ejecutivos.

## Sistema de Secciones Inteligente

IA Work Generator incorpora un sistema de identificación jerárquica de contenido que permite segmentar y etiquetar cada componente del informe: títulos, subtítulos y párrafos. Cada sección generada queda registrada con un identificador estructural que vincula su contenido subordinado (por ejemplo, el texto bajo "Introducción") de forma explícita. Esta arquitectura semántica permite al usuario realizar consultas o acciones dirigidas con precisión quirúrgica, tales como "modifica el texto de la introducción", "elimina la conclusión" o "cuántos caracteres tiene el desarrollo".

El motor de generación, respaldado por un parser jerárquico, analiza la estructura del documento y permite al asistente interactuar con la jerarquía del texto en tiempo real. Esto habilita funcionalidades avanzadas como recuento de secciones, evaluación de longitud por área temática, reemplazo contextual selectivo y visualización estructurada para su edición individual o masiva.

## Tecnologías Empleadas

El frontend utiliza Tauri, React, TailwindCSS y ShadCN UI, proporcionando una interfaz ligera y moderna. El backend se basa en FastAPI, con orquestación de modelos mediante LangChain. Ollama gestiona la ejecución eficiente de los modelos LLM locales y ChromaDB ofrece las capacidades de indexación semántica.

## Inteligencia Adaptativa

En ausencia de GPU, el sistema recurre a modelos cuantizados como Mistral o Mixtral, gestionando la generación por bloques para minimizar el uso de recursos. Si detecta una GPU (CUDA o Metal), activa la aceleración por hardware, mejorando notablemente los tiempos de inferencia sin comprometer la coherencia narrativa.

## Arquitectura Modular

El proyecto se organiza en componentes independientes que facilitan su mantenimiento y extensión:

* **frontend/**: Interfaz de usuario.
* **backend/**: Lógica central como API REST.
* **resources/**: Plantillas editables.
* **config/**: Configuraciones del sistema.
* **historial.json**: Repositorio local con metadatos.
* **agents.md**: Documentación interna de agentes lógicos.

## Flujo de Usuario

1. **Asistente de contexto**: Recoge información clave y propone estructura.
2. **Generación animada**: Redacción progresiva por secciones.
3. **Editor interactivo**: Revisión y ajustes.
4. **Exportación y registro**: Guardado con metadatos.

## Esquemas Funcionales

### Flujo de Usuario

Inicio de aplicación ↓ Asistente de contexto ↓ Generación por secciones ↓ Editor interactivo ↓ Exportación ↓ Registro en historial

### Arquitectura Técnica

Frontend (Tauri/React) ↔ Backend (FastAPI/LangChain/Ollama) → Pandoc/Sistema de Archivos

### Módulos Lógicos

Agente de Contexto → Generador de Texto → Editor Interactivo → Exportador de Documento
↑                                         ↓                            ↓
Motor Semántico (Chroma) ← Historial Persistente   Plantillas y Configuración

## Instrucciones de Despliegue

### Backend

```bash
ollama run mixtral
ollama serve &
ollama pull mixtral  # en caso de error
ollama pull mistral  # para equipos con pocos recursos
```

Modificar `config/config.yaml` si se usa Mistral. Luego:

```bash
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r backend/requirements.txt
pip install -U langchain-community sentence-transformers
```

Instalar Pandoc:

```bash
sudo apt-get install pandoc  # Linux
brew install pandoc          # macOS
```

Ejecutar backend:

```bash
python backend/main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Pruebas y Distribución

Ejecución de pruebas:

```bash
pytest
```

Compilación y empaquetado:

```bash
sh backend/build.sh
npm run tauri build
```

## Perspectiva de Evolución

Se prevé la personalización completa de plantillas, exportación a .pptx y .xlsx, integración con Power BI, soporte multilingüe y adaptación a sectores como ingeniería, medicina o derecho. Asimismo, se contempla un backend totalmente autónomo sin dependencias externas.

## Licencia

MIT – Uso libre con atribución al autor original.
