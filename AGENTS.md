# Guía Operativa de Agentes

Este documento describe, con alcance integral, los procedimientos para crear, modificar y mantener los agentes lógicos que sustentan IA Work Generator tanto en el backend como en el frontend. Al diferenciarse de la documentación arquitectónica —ubicada en `docs/architecture/architecture.md`—, su enfoque es eminentemente instrumental y está dirigido al desarrollador que necesite intervenir en el código fuente con rapidez y criterios uniformes.

## Filosofía de diseño y alcance común

Los agentes representan unidades autocontenidas de responsabilidad única y exponen una interfaz explícita que define entradas, salidas y efectos colaterales aceptables. Este patrón se replica en ambos extremos de la aplicación: en el backend como coroutines Python y en el frontend como hooks o servicios React. En cada caso se impone la transparencia operacional: toda acción ejecutada por un agente se registra en logs estructurados para su auditoría y se acompaña de eventos normalizados publicados en un bus asíncrono, lo que permite el desacoplamiento sin renunciar a la trazabilidad.

## Backend: convenciones y flujo de trabajo

El código de cada agente backend reside en `backend/agents/<nombre_del_agente>/`. El módulo principal se llama `core.py` y su clase pública deriva de `BaseAgent`, implementando la firma `run(payload: dict) -> dict`. Los parámetros ajustables se agrupan en `config.py`. Las pruebas unitarias se ubican en `tests/agents/` siguiendo la misma convención nominal; por ejemplo, las pruebas de `context_agent` se almacenan en `tests/agents/test_context_agent.py`. El pipeline de integración continua ejecuta `pytest` con cobertura mínima del setenta y cinco por ciento. La comunicación interna usa un bus basado en `asyncio.Queue` y cada agente documenta los eventos que consume y produce para evitar acoplamientos ocultos. El log se produce mediante `get_structured_logger`, que serializa en JSON y añade metadatos de sesión.

## Frontend: agentes de interfaz y pautas de integración

El concepto de agente se materializa en el frontend como servicios React aislados que encapsulan lógica de interacción, orquestación de llamadas REST al backend y gestión de estado derivado. Cada agente frontend vive en `frontend/src/agents/<NombreDelAgente>/` y expone un hook principal con nomenclatura `use<NombreDelAgente>()`. Dicho hook devuelve un objeto cuyas claves reflejan acciones y estados observables. La comunicación con el backend se realiza mediante `fetch` o `axios` envueltos en un wrapper `request.ts` que incorpora control de cancelación, reintentos y serialización de errores. El estado se mantiene con Zustand; los agentes no deben manipular el contexto global directamente, sino a través de acciones tipadas definidas en sus propios stores. Las pruebas se escriben con Vitest y React Testing Library en `frontend/tests/agents/`, utilizando mocks de red para aislar la lógica de presentación.

En cuanto al patrón visual, cualquier componente que dependa de un agente debe recibir sus props desde el hook y abstenerse de instanciarlo internamente para favorecer la inyección de dependencias y la testabilidad. El estilo se implementa con TailwindCSS; los componentes usan shadcn/ui exclusivamente para artefactos básicos, evitando escribir HTML sin estilado centralizado. Cada agente frontend documenta los eventos que escucha, normalmente a través de WebSockets cuando se requiere actualización en tiempo real. La serialización de eventos respeta el esquema JSON definido en `frontend/src/protocols/events.ts`.

## Registro, observabilidad y métricas cruzadas

Tanto en backend como en frontend, los agentes deben invocar el sistema de telemetría unificado mediante la función `track_event(event_name, payload)`. Esto alimenta la consola de observabilidad que corre en modo local, permitiendo al desarrollador inspeccionar trazas, latencias y errores en un tablero Grafana configurado para esta solución. Los eventos de tipo `agent_error` desencadenan alertas sonoras y se almacenan con prioridad alta en el log local cifrado. Esta práctica permite al equipo mantener una visión holística del desempeño del sistema sin exponer datos fuera del entorno local.

## Ciclo de despliegue y versionado

La incorporación de un agente backend nuevo exige incrementar la versión menor del paquete, mientras que romper contratos públicos escala a versión mayor. En el frontend, la adición de un agente con impacto visible en la UI eleva la versión de la aplicación Tauri en el mismo patrón semántico. Durante la fase de `tauri build`, un script verifica la paridad de versiones entre frontend y backend; cualquier divergencia detiene la compilación hasta que se sincronicen los números.

## Eliminación de agentes y gobernanza del código

La retirada de un agente implica un pull request acompañado de justificación y pruebas que demuestren la equivalencia funcional tras la migración de responsabilidades. No se aprueban eliminaciones que reduzcan la cobertura de pruebas. El mismo PR debe actualizar el esquema de eventos, la configuración YAML y la documentación pertinente.

## Configuración y validación de parámetros

Los parámetros configurables de backend residen en `config/config.yaml`. En frontend, los defaults se hallan en `frontend/src/config/defaults.ts`. Toda modificación se valida mediante el script `backend/tools/validate_config.py` y su contraparte `frontend/scripts/validate_env.ts`, con ejecución automática en el pipeline CI.

## Conclusión

Con este compendio se cubren las dos caras de la arquitectura de agentes, garantizando un ecosistema coherente desde la lógica de servidor hasta la interacción de usuario. La adhesión a estas directrices preserva la robustez, mantenibilidad y extensibilidad del proyecto, alineándose con nuestro compromiso de ofrecer una solución local eficiente y confiable.
