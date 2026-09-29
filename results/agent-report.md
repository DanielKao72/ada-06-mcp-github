# Reporte del Agente — Customer Search

## Agente / Versión
- **Agente / Modelo:** Antigravity (Google DeepMind) / Gemini 3.7 Flash
- **Repositorio:** `ada-05-spec-driven-feature`
- **Stack Tecnológico:** Python 3.11, FastAPI, Pydantic v2, pytest, httpx, Uvicorn

---

## Contexto Inicial
El proyecto se inició como un repositorio limpio y vacío con el objetivo de aplicar *Spec-Driven Development*. El requerimiento principal consistió en implementar la funcionalidad de **Customer Search** (búsqueda de clientes por coincidencia parcial en nombre o correo electrónico, insensible a mayúsculas/minúsculas y con validaciones), utilizando persistencia en un archivo JSON local y una suite de pruebas automatizadas con `pytest`.

---

## Secuencia de Tareas

### T-01: Configuración del Proyecto (Project Setup)
* **Qué hizo el agente:**
  - Creó [requirements.txt](../requirements.txt) con las dependencias necesarias (`fastapi`, `uvicorn[standard]`, `pydantic[email]`, `pytest`, `httpx`).
  - Creó la estructura de directorios (`app/`, `app/core/`, `data/`).
  - Implementó [app/core/config.py](../app/core/config.py) configurando la ruta por defecto hacia `data/customers.json`.
  - Instaló las dependencias en el entorno de ejecución.
* **Revisión humana:** Aprobé la estructura y dependencias mínimas para que el agente pueda empezar con el desarrollo.
* **Tests:** Se verificó que las importaciones sean exitosas con `python -c "import fastapi, pydantic, pytest, httpx"`.

### T-02: Modelo de Dominio (Domain Model)
* **Qué hizo el agente:**
  - Implementó en [app/schemas/customer.py](../app/schemas/customer.py) los modelos Pydantic: `CustomerBase`, `CustomerCreate`, `Customer` y `CustomerResponse`..
* **Revisión humana:** Aprobé los modelos de datos.
* **Tests:** Se crearon 5 pruebas unitarias en `tests/test_domain_models.py`.

### T-03: Lógica de Búsqueda y Persistencia (Search Logic)
* **Qué hizo el agente:**
  - Creó la excepción [CustomerAlreadyExistsError](../app/core/exceptions.py).
  - Implementó [JsonCustomerRepository](../app/repositories/json_customer_repository.py) con la búsqueda insensible a mayúsculas/minúsculas por coincidencia de subcadena en `name` o `email`.
  - Implementó [CustomerService](../app/services/customer_service.py) para remover espacios en blanco y validar la duplicación de emails.
* **Revisión humana:** Aprobé que se haya implementado la persistencia JSON local como solicité al inicio del análisis con el agente.
* **Tests:** Se crearon 7 pruebas unitarias en `tests/test_json_customer_repository.py` y `tests/test_customer_service.py`.

### T-04: Capa de Validación y Errores HTTP (Validation and Errors)
* **Qué hizo el agente:**
  - Implementó la inyección de dependencias en [app/dependencies.py](../app/dependencies.py).
  - Creó el router [app/routers/customer_router.py](../app/routers/customer_router.py) con validación estricta de parámetros de consulta ($2 \le \text{longitud} \le 100$) y endpoints para `GET /search`, `POST /customers` y `GET /customers`.
  - Inicializó la aplicación FastAPI en [app/main.py](../app/main.py) con endpoint de salud `/health`.
  - Configuró `tests/conftest.py` con fixtures para aislar el almacenamiento JSON mediante `tmp_path`.
* **Revisión humana:** Aprobado el diseño de la API REST y manejo de códigos HTTP (`200`, `201`, `409`, `422`).
* **Tests:** Creado `tests/test_customer_api_validation.py` (6 pruebas de integración superadas).

### T-05: Suite Completa de Pruebas Automatizadas (Tests)
* **Qué hizo el agente:**
  - Implementó [tests/test_customer_search_api.py](../tests/test_customer_search_api.py) cubriendo directamente todos los criterios de aceptación (`AC-01` a `AC-07`) y escenarios de prueba (`TS-01` a `TS-10`).
  - Validó casos de búsqueda por prefijo, sufijo, dominio de correo, insensibilidad a mayúsculas, recorte de espacios, límites de caracteres, resultados vacíos y creación con duplicados.
* **Revisión humana:** Revisé que se hayan realizado todos (o varios) de los casos de prueba para la búsqueda.
* **Tests:** Ejecutó la suite completa con 27 pruebas pasando al 100%.

### T-06: Documentación Técnica (Documentation)
* **Qué hizo el agente:**
  - Actualizó [README.md](../README.md) con la descripción del servicio, estructura del proyecto, instrucciones de instalación, arranque con Uvicorn, ejecución de pruebas con `pytest` y ejemplos detallados de comandos `curl` para cada endpoint.
* **Revisión humana:** Le dí la instrucción de qué incluir en el README y aprobé las secciones que iba a documentar.

---

## Problemas Encontrados y Soluciones
1. No se encontraron problemas en la implementación de las funcionalidades y todas las pruebas pasaron exitosamente.

---

## Intervenciones Humanas
1. **Ajuste de persistencia:** Al inicio el agente interpretó que la persistencia se iba a hacer con una base de datos, así que intervine para dejar claro que iba a ser meidante un archivo JSON local (`data/customers.json`).
2. **Estructura de Requerimientos Funcionales:** Le definí al agente una estructura para redactar los requisitos funcionales de tal manera que sean medibles (*Source, Stimulus, Artifact, Environment, Response, Measure*) [REQUIREMENTS.md](../REQUIREMENTS.md).

---

## Cambios en Requerimientos / Especificación
* **Cambio de persistencia a JSON local:** Debido a que el agente interpretó que se usaría una base de datos. Modifiqué las especificaciones  [SPEC.md](../SPEC.md), [ARCHITECTURE.md](../ARCHITECTURE.md) y [TASKS.md](../TASKS.md) para reflejar que no se requieren bases de datos.
* **Regla de email único:** Incluí la especificación de retornar un HTTP `409 Conflict` ante intentos de registrar correos duplicados.

---

## Verificación Final
La suite completa de pruebas automatizadas fue ejecutada exitosamente:

```
tests\test_customer_api_validation.py ......                             [ 22%]
tests\test_customer_search_api.py .........                              [ 55%]
tests\test_customer_service.py ...                                       [ 66%]
tests\test_domain_models.py .....                                        [ 85%]
tests\test_json_customer_repository.py ....                              [100%]

======================== 27 passed, 1 warning in 1.92s ========================
```

---

## Lecciones Aprendidas
1. El *Spec-Driven Development* ahorra tiempo y evita hacer trabajo de más. Lo importante de esta metodología es contar con requisitos claros (por ello pedí un formato de 6 partes para los requisitos), una especificación detallada con criterios *Given-When-Then* y un plan de arquitectura con diagramas antes de codificar garantiza que cada módulo implementado cumpla con precisión su propósito sin inventar requerimientos sobre la marcha.
