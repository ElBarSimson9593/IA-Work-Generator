# Guía Operativa de Agentes

Este documento, alojado en la raíz del repositorio como `AGENTS.md`, tiene el cometido de describir los procedimientos concretos para crear, modificar y mantener los agentes lógicos que sustentan IA Work Generator. Al diferenciarse de la documentación arquitectónica —trasladada a `docs/architecture/architecture.md`—, su enfoque es eminentemente instrumental y va dirigido al desarrollador que necesite intervenir en el código fuente con rapidez y criterio consistente.

## Alcance y filosofía de diseño

Los agentes representan unidades autocontenidas de responsabilidad única. Cada uno expone una interfaz explícita que define entradas, salidas y efectos colaterales aceptables. Esta segmentación obedece al principio de responsabilidad única y facilita que la inteligencia colectiva del sistema evolucione de forma incremental sin comprometer la estabilidad global. La regla rectora es conservar la transparencia operacional, de modo que cualquier acción ejecutada por un agente debe quedar registrada en logs estructurados para su posterior auditoría.

## Ubicación del código

Todo agente reside, de manera individual, bajo el espacio `backend/agents/`. El nombre de la carpeta y del módulo Python debe reflejar su responsabilidad, por ejemplo `context_agent/` o `export_agent/`. Dentro de cada módulo, el archivo `config.py` define los parámetros ajustables, mientras que `core.py` contiene la implementación de la lógica principal. Las pruebas unitarias se ubican en `tests/agents/`, siguiendo la misma convención de nombres; por ejemplo, las pruebas de `context_agent` se alojan en `tests/agents/test_context_agent.py`.

## Flujo de trabajo recomendado

Cuando se crea un agente nuevo, el procedimiento arranca con la formulación de su contrato público. Dicho contrato se codifica como una clase derivada de `BaseAgent`, que impone la firma estándar `run(payload: dict) -> dict`. Una vez definida, se confecciona un stub mínimo que únicamente lanza una excepción de “NotImplemented”. Posteriormente, se redactan las pruebas unitarias que ejerciten los casos nominales y los bordes funcionales. Con ese andamiaje se procede a implementar la lógica real, respetando las directrices de estilo PEP 8 y las prácticas de programación defensiva.

## Integración con el bus de eventos

La comunicación entre agentes se realiza mediante un bus asíncrono basado en `asyncio.Queue`. Para suscribirse a un tipo de evento concreto, el agente implementa la rutina `subscribe(self, event_type: str)`. La emisión de eventos se lleva a cabo a través de la llamada `publish(event: Event)` que acepta un objeto serializable. Cuando se añade un agente nuevo, es imperativo documentar en su docstring qué eventos consume y cuáles produce, con el fin de mantener la trazabilidad y evitar acoplamientos ocultos.

## Registro y observabilidad

Cada agente debe inicializar un logger propio mediante la utilidad `get_structured_logger(name)`, que formatea las entradas en JSON y captura contexto adicional como la huella temporal, el identificador de sesión y el nivel de severidad. No se permite la impresión directa por consola fuera del logger. Los mensajes de nivel inferior a `DEBUG` se reservan para diagnósticos y no deben persistir en entornos de producción salvo indicación contraria.

## Ciclo de pruebas

El pipeline de integración continua ejecuta `pytest` con la bandera `--strict-markers` y `--cov=backend/agents/`. Cualquier agente incorporado que reduzca la cobertura global por debajo del umbral configurado —actualmente setenta y cinco por ciento— detendrá el despliegue. Las pruebas deben aislarse de recursos externos y, cuando ello resulte imposible, simular la dependencia mediante fixtures.

## Despliegue y versionado

La introducción de un agente nuevo implica un incremento menor en la versión semántica del paquete backend, por ejemplo de `2.3.1` a `2.4.0`. Si el cambio afecta contratos públicos o esquemas de eventos, el salto es mayor y se documenta en `CHANGELOG.md`. El despliegue se orquesta mediante el script `scripts/release_backend.sh` que etiqueta el commit, actualiza los artefactos y dispara la compilación en Tauri.

## Eliminación de agentes

La retirada de un agente requiere una proposición de mejora (PR) que justifique su obsolescencia y describa la migración de sus responsabilidades. Se acepta únicamente cuando existe cobertura de pruebas que demuestre la equivalencia funcional tras la remoción. El PR debe referenciar la actualización de configuración y la limpieza del historial semántico pertinente.

## Consulta rápida de parámetros

Los ajustes configurables de cada agente se documentan en `config/config.yaml` bajo la clave con su nombre. Para modificarlos, se edita el YAML con cuidado de no romper la validación de esquema; cualquier inconsistencia detendrá la carga del backend. El comando `python backend/tools/validate_config.py` permite verificar la integridad antes de confirmar el commit.

## Conclusión

Este archivo establece un marco operativo uniforme y reproducible para la gestión del ciclo de vida de los agentes. Siguiendo estas pautas, el equipo de desarrollo preservará la robustez y extensibilidad del sistema, alineándose con la misión estratégica de proveer una solución local, eficiente y confiable.
