# AI Usage Log

### Entrada 1: Análisis de Requisitos y Selección de Persistencia
* **Etapa:** Requisitos y Análisis Inicial
* **Qué propuso la IA:**
  - La IA propuso un esquema de persistencia relacional completa utilizando SQLAlchemy ORM, migraciones y una base de datos SQLite/PostgreSQL.
* **Qué decisión tomó el estudiante:**
  - Decidí cambiar la persistencia con una base de datos por una de archivo JSON local.
* **Qué cambió en el producto:**
  - Se descartaron las dependencias de base de datos relacionales (`SQLAlchemy`, conectores de base de datos).
  - Se diseñó un repositorio específico ([app/repositories/json_customer_repository.py](app/repositories/json_customer_repository.py)) con soporte de inicialización automática y filtrado en memoria por subcadenas.

---

### Entrada 2: Estructuración Formal de Requerimientos y Especificación Técnica
* **Etapa:** Especificación de Requisitos
* **Qué propuso la IA:**
  - Una redacción preliminar de [REQUIREMENTS.md](REQUIREMENTS.md) con descripciones textuales de las funciones de búsqueda y validación.
* **Qué decisión tomó el estudiante:**
    1. Pedí reestructurar todos los Requerimientos Funcionales bajo el formato de 6 partes: *Source, Stimulus, Artifact, Environment, Response, Measure*.
* **Qué cambió en el producto:**
  - Se reescribió [REQUIREMENTS.md](REQUIREMENTS.md) con los requisitos `FR-01` a `FR-06` modelados con el formato que especifiqué.

---

### Entrada 3: Diseño de Arquitectura y Planificación Atómica de Tareas
* **Etapa:** Arquitectura y Plan de Tareas
* **Qué propuso la IA:**
  - Un diagrama de componentes y de secuencia basado en lo descrito en [ARCHITECTURE.md](ARCHITECTURE.md).
* **Qué decisión tomó el estudiante:**
    1. Pedí incorporar diagramas con Mermaid en [ARCHITECTURE.md](ARCHITECTURE.md) para visualizar la arquitectura de capas y la secuencia del flujo de búsqueda. Solicité esta tarea porque era más rápido describirle mi diseño y que me creara un diagrama Mermaid inicial.
* **Qué cambió en el producto:**
  - [ARCHITECTURE.md](ARCHITECTURE.md) se modificó al añadir un diagrama de componentes y un diagrama de secuencia.

---

### Entrada 4: Implementación
* **Etapa:** Implementación y Pruebas
* **Qué propuso la IA:**
  - Ejecutar estrictamente el protocolo de [AGENTS.md](AGENTS.md): ejecutar `pytest` antes y después de cada cambio, implementar únicamente la tarea en curso.
  - Implementó todas las tareas descritas en [TASKS.md](TASKS.md) como `T-04` (FastAPI router, validación y error handlers), `T-05` (suite de pruebas completa) y `T-06` (documentación en [README.md](README.md)).
* **Qué decisión tomó el estudiante:**
  - Validé y autoricé el avance incremental tarea por tarea.
* **Qué cambió en el producto:**
  - Código fuente completo creado en `app/` (`config.py`, `schemas/customer.py`, `repositories/json_customer_repository.py`, `services/customer_service.py`, `routers/customer_router.py`, `dependencies.py`, `main.py`).
  - Suite de 27 pruebas automatizadas (`tests/`) ejecutadas con `pytest -v` alcanzando el 100% de éxito.