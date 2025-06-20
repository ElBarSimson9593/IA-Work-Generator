# IA Work Generator — Generador de Informes con IA Local

IA Work Generator es una aplicación de escritorio autárquica diseñada para orquestar la redacción de informes extensos en contextos académicos y corporativos. El énfasis estratégico gravita en la soberanía de los datos y en la eficiencia operativa: toda la inferencia se ejecuta sobre modelos de lenguaje residentes en el propio equipo, de modo que se erradican las dependencias de servicios en la nube. El motor adapta su consumo de recursos a la disponibilidad de GPU o CPU, priorizando la velocidad de inferencia sin sacrificar la coherencia discursiva.

## Propuesta de Valor

Al iniciar la aplicación, el usuario se enfrenta a un asistente dialógico que define extensión, propósito, tono y audiencia del documento. Confirmado el contexto, la generación avanza sección por sección; la interfaz reproduce la escritura en tiempo real para reforzar la percepción de trazabilidad. En cualquier momento el usuario puede intervenir mediante un editor enriquecido antes de exportar el resultado a DOCX o PDF, operativa soportada por Pandoc. El historial de entregables se conserva en un repositorio estructurado con búsqueda semántica impulsada por ChromaDB, y la arquitectura modular facilita evoluciones como la exportación a presentaciones, hojas de cálculo o cuadros de mando.

## Sistema de Secciones Inteligente

Cada componente del informe —títulos, subtítulos y párrafos— se etiqueta con un identificador jerárquico inmutable. Este esquema semántico posibilita operaciones de precisión milimétrica, por ejemplo modificar una introducción concreta, suprimir la conclusión o auditar la longitud de un desarrollo. Un parser jerárquico inspecciona la estructura mientras el usuario edita, habilitando métricas dinámicas, sustituciones contextuales y visualizaciones segmentadas.

## Pila Tecnológica

El frontend, construido con Tauri, React, TailwindCSS y ShadCN UI, ofrece una interfaz ligera y responsiva. El backend, en FastAPI, delega la orquestación de modelos locales a LangChain, mientras que Ollama gestiona la carga eficiente de LLM cuantizados o de precisión completa. ChromaDB provee indexación semántica de alta velocidad. Todo el ecosistema opera desconectado de internet, manteniendo la integridad de la propiedad intelectual.

## Inteligencia Adaptativa

En ausencia de GPU, la aplicación recurre de forma transparente a modelos cuantizados como Mistral o Mixtral y fragmenta la generación en bloques para contener el consumo de memoria. Si detecta una GPU compatible con CUDA o Metal, activa la aceleración por hardware y comprime los tiempos de respuesta manteniendo la cohesión argumental.

## Arquitectura Modular

El proyecto se distribuye en un frontend responsable de la experiencia de usuario, un backend que expone la API REST y la lógica de generación, un conjunto de plantillas parametrizables, un almacén de configuraciones y un historial local que preserva tanto los documentos finales como sus metadatos. La documentación interna de los agentes lógicos reside en `agents.md`, mientras que los parámetros persistentes del sistema se ubican en `config/config.yaml`.

## Experiencia de Usuario

El recorrido típico comienza con el asistente contextual, continúa con la redacción animada por secciones, pasa a la fase de edición interactiva y culmina con la exportación del documento y su inscripción automática en el historial. Todo el flujo se ejecuta sin fricciones y con pleno control por parte del usuario final.

## Despliegue

Antes de compilar, asegúrese de disponer de Ollama y Pandoc en el sistema anfitrión. El backend requiere un entorno virtual de Python y las dependencias especificadas en `backend/requirements.txt`. Una vez instaladas, lance `backend/main.py`. El frontend se inicia desde la carpeta `frontend` mediante `npm install` y `npm run dev`. Para distribución, ejecute las pruebas con `pytest`, compile el backend con `sh backend/build.sh` y empaquete la aplicación de escritorio vía `npm run tauri build`.

### Pasos rápidos (shell)

```bash
# Modelos
ollama pull mixtral          # recomendado
ollama pull mistral          # alternativa para hardware limitado
ollama serve &

# Backend
python -m venv venv
source venv/bin/activate      # en Windows use venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -U langchain-community sentence-transformers
python backend/main.py

# Frontend
cd frontend
cp .env.example .env  # opcional: ajusta VITE_API_URL si es necesario
npm install
npm run dev
```

## Hoja de Ruta

Las próximas iteraciones contemplan plantillas personalizables, exportación a .pptx y .xlsx, integración nativa con Power BI, localización multilingüe y ajustes sectoriales para ingeniería, medicina y derecho. También se proyecta un backend plenamente autónomo, sin dependencias externas, para fortalecer la resiliencia operativa.

## Licencia

MIT. Uso libre con atribución al autor.
