# GitHub MCP Engineering Review — ADA-06

## 1. Repositorio

Owner/Repo: `DanielKao72/ada-06-mcp-github`

Visibilidad: Pública

Rama analizada:
- `master` (base)
- `feature/customer-update-delete` (head del PR #2)

## 2. Conexión MCP

Server: GitHub MCP Server

Modo: READ-ONLY.

Toolsets:
- repos
- issues
- pull_requests

### Capacidades del MCP usadas

Todas las llamadas se limitaron a `owner=DanielKao72`, `repo=ada-06-mcp-github`.

| # | Tool | Toolset | Parámetros relevantes | Propósito |
| --- | --- | --- | --- | --- |
| 1 | `get_file_contents` | repos | `/`, `app`, `app/core`, `tests`, `docs`, `data` | Listar la estructura de directorios |
| 2 | `get_file_contents` | repos | `README.md`, `ARCHITECTURE.md`, `requirements.txt` | Entender propósito, arquitectura y dependencias |
| 3 | `get_file_contents` | repos | `app/main.py`, `app/dependencies.py`, `tests/conftest.py` | Identificar el entry point, la inyección de dependencias y los fixtures |
| 4 | `get_file_contents` | repos | `app/repositories/json_customer_repository.py` con `ref=feature/customer-update-delete` | Revisar el repositorio JSON completo en la rama del PR |
| 5 | `list_branches` | repos | — | Identificar ramas |
| 6 | `list_commits` | repos | `sha=feature/customer-update-delete` | Ver el historial de commits del PR |
| 7 | `list_issues` | issues | — | Localizar el Issue seleccionado |
| 8 | `issue_read` | issues | `issue_number=1`, `method=get` | Leer requisitos y criterios de aceptación del Issue |
| 9 | `list_pull_requests` | pull_requests | `state=all` | Localizar el PR seleccionado |
| 10 | `pull_request_read` | pull_requests | `pullNumber=2`, `method=get` | Leer los metadatos del PR |
| 11 | `pull_request_read` | pull_requests | `pullNumber=2`, `method=get_files` | Leer los archivos modificados y sus diffs |
| 12 | `pull_request_read` | pull_requests | `pullNumber=2`, `method=get_check_runs` | Verificar el estado de CI |

## 3. Entendimiento del Repositorio

### Propósito

*Customer Search Service*: microservicio REST en **FastAPI + Pydantic v2** para crear, listar y buscar clientes por subcadena del nombre o del email. La búsqueda no distingue mayúsculas y recorta espacios. Los datos persisten en un archivo JSON local (`data/customers.json`), sin base de datos externa. El repositorio proviene de la ADA-05 (commit inicial: *"start repository with all files in ada-05-sprec-driven-feature repository"*) y sigue un flujo *spec-driven*: `REQUIREMENTS.md` → `SPEC.md` → `TASKS.md` → código → tests.

### Resumen de la arquitectura

Arquitectura en capas con inyección de dependencias:

```
HTTP Client → Router (FastAPI) → Service (reglas de negocio) → JsonCustomerRepository → data/customers.json
                  ↑                      ↑
          Pydantic schemas     dependencies.py / core/config.py
```

### Directorios principales y archivos importantes

| Ruta | Contenido |
| --- | --- |
| `app/main.py` | **Entry point**: factory `create_app()`, registra el router y `GET /health`; expone `app` para `uvicorn app.main:app` |
| `app/dependencies.py` | Proveedores de DI: `get_customer_repository()` y `get_customer_service()` |
| `app/core/config.py` | Settings (nombre, versión, ruta del JSON) |
| `app/core/exceptions.py` | Excepciones de dominio (`CustomerAlreadyExistsError`) |
| `app/schemas/customer.py` | Modelos Pydantic: `CustomerBase`, `CustomerCreate`, `Customer`, `CustomerResponse` |
| `app/repositories/json_customer_repository.py` | I/O del archivo JSON, búsqueda y filtrado |
| `app/services/customer_service.py` | Normalización de consultas y unicidad de email |
| `app/routers/customer_router.py` | Endpoints `/api/v1/customers` |
| `data/` | Solo `.gitkeep`; `customers.json` se crea en tiempo de ejecución |
| `tests/` | Suite de pytest |
| `REQUIREMENTS.md`, `SPEC.md`, `ARCHITECTURE.md`, `TASKS.md`, `AGENTS.md` | Documentación spec-driven y reglas para agentes |

### Entry points de la aplicación

- `app/main.py` → `app = create_app()`, que se ejecuta con `uvicorn app.main:app --reload --port 8000`.
- Endpoints en `master`: `GET /health`, `POST /api/v1/customers`, `GET /api/v1/customers`, `GET /api/v1/customers/search?q=`.

### Componentes/módulos importantes

| Componente | Responsabilidad |
| --- | --- |
| `customer_router` | Transporte HTTP, binding de parámetros y mapeo de excepciones a 409/422 |
| `CustomerService` | `search_customers`, `create_customer`, `get_all_customers` |
| `JsonCustomerRepository` | `get_all`, `get_by_id`, `get_by_email` (case-insensitive), `search`, `save` |
| Schemas Pydantic | Validación (nombre no vacío y ≤150 caracteres, `EmailStr`) y serialización |

### Pruebas

Framework: `pytest` + `httpx` (`TestClient`). En `tests/conftest.py`, el fixture `test_repo` usa `tmp_path` para aislar el archivo JSON y el fixture `client` sustituye `get_customer_repository` mediante `app.dependency_overrides`.

| Archivo | Nivel |
| --- | --- |
| `test_domain_models.py` | Unitario: schemas |
| `test_json_customer_repository.py` | Unitario: repositorio |
| `test_customer_service.py` | Unitario: servicio |
| `test_customer_api_validation.py` | Integración: códigos de estado y errores |
| `test_customer_search_api.py` | End-to-end: escenarios de búsqueda (TS-01..TS-10) |

Según el Issue y `docs/tracebility.md`, `master` tiene **27 tests**.

### Documentación relevante

- `README.md`: instalación, ejecución y ejemplos `curl` de cada endpoint.
- `ARCHITECTURE.md`: diagramas Mermaid, interfaces, manejo de errores y trade-offs.
- `REQUIREMENTS.md` / `SPEC.md`: Requerimientos funcionales (FR-01..FR-06), requerimientos no funcionales (NFR-01..NFR-03), criterios de aceptación (AC-01..AC-07) y tareas (TS-01..TS-10).
- `TASKS.md`: T-01..T-06.

## 4. Análisis del Issue

Issue: [#1 — feat: Add Customer Update (PATCH) and Deletion (DELETE) Endpoints](https://github.com/DanielKao72/ada-06-mcp-github/issues/1) 

### Hechos del issue

- `PATCH /api/v1/customers/{customer_id}` debe actualizar `name`, `email` o ambos. `id` y `created_at` son inmutables. Responde 200, 404, 409 (email de otro cliente) o 422.
- `DELETE /api/v1/customers/{customer_id}` responde 204 si elimina el registro o 404 si el ID no existe.
- Define los criterios de aceptación AC-01..AC-05 en formato Gherkin.
- Capas impactadas: schema `CustomerUpdate`, `CustomerNotFoundError`, `update()`/`delete()` en el repositorio, lógica en el servicio, rutas en el router, tests y documentación (`SPEC.md`, `README.md`).
- DoD: respetar la arquitectura en capas, hacer pasar los tests nuevos y mantener los 27 existentes.

### Ambigüedades

- No aclara si un `PATCH` con el **mismo email actual** del cliente debe dar 409 o 200. El PR eligió 200.
- No aclara si enviar `id`/`created_at` en el body debe **ignorarse** o **rechazarse**. El PR eligió rechazar con 422 (`extra="forbid"`).
- No aclara si un valor explícito `null` en `name`/`email` es válido. El PR lo rechaza con 422.
- No aclara si la comparación de emails para detectar colisiones distingue mayúsculas. El PR usa `get_by_email`, que es case-insensitive.
- Los AC del Issue están numerados AC-01..AC-05, pero esos IDs ya existen en `SPEC.md`. El PR los renumeró a AC-08..AC-12.

### Requisitos/especificaciones relacionadas

`SPEC.md` en `master` lista explícitamente *"Customer modification (PUT/PATCH) and deletion (DELETE)"* como **Out of Scope**. El Issue exige cambiar ese alcance.

### Código relacionado

Archivos afectados por el Issue:

- `app/schemas/customer.py`
- `app/core/exceptions.py`
- `app/repositories/json_customer_repository.py`
- `app/services/customer_service.py`
- `app/routers/customer_router.py`

### Pruebas relacionadas

`tests/test_domain_models.py`, `tests/test_json_customer_repository.py`, `tests/test_customer_service.py` y un nuevo test end-to-end de API.

## 5. Revisión del Pull Request

PR: [#2 — Feature/customer update delete](https://github.com/DanielKao72/ada-06-mcp-github/pull/2): open, `feature/customer-update-delete` → `master`, 3 commits, 15 archivos.

### Comportamiento modificado

- Nuevo endpoint `PATCH /api/v1/customers/{customer_id}`.
- Nuevo endpoint `DELETE /api/v1/customers/{customer_id}`, que responde `204` con `Response` vacío.
- Nuevo schema `CustomerUpdate` con `extra="forbid"`. Exige al menos un campo y prohíbe `null` explícito.

### Archivos modificados

| Tipo | Archivos |
| --- | --- |
| Código | `app/schemas/customer.py`, `app/core/exceptions.py`, `app/repositories/json_customer_repository.py`, `app/services/customer_service.py`, `app/routers/customer_router.py` |
| Tests | `tests/test_domain_models.py`, `tests/test_json_customer_repository.py`, `tests/test_customer_service.py`, `tests/test_customer_update_delete_api.py` (nuevo) |
| Docs | `REQUIREMENTS.md`, `SPEC.md`, `ARCHITECTURE.md`, `TASKS.md` (T-07), `README.md`, `docs/tracebility.md` |

### Pruebas

- Tests agregados: 10 en schemas, 2 en repositorio, 4 en servicio y 16 en API. Son 32 nuevos, por lo que serían 59 pruebas en todo el proyecto (27 antes del cambio).

### Observaciones

- El diseño respeta la arquitectura en capas Schema → Repository → Service → Router y no toca `dependencies.py` ni `main.py`.
- La documentación se actualizó de forma consistente en los seis archivos.
- Los mensajes de los commits `14cd359` y `caae615` son casi idénticos, lo que hace el historial poco descriptivo.

### Riesgos

- **Escritura no atómica:** `_write_raw_data` abre el archivo con `"w"` directamente, sin archivo temporal ni rename. Una interrupción a mitad de la escritura corrompe el JSON. `ARCHITECTURE.md` afirma "atomic file read/writes", lo cual no coincide con el código.


### Preguntas

- ¿Se acepta rechazar `id`/`created_at` con 422 en lugar de ignorarlos? El Issue solo dice "remain immutable".
- ¿Debería el PR usar `Closes #1` para enlazar formalmente el Issue?
- ¿Se planea agregar CI (GitHub Actions con `pytest`) para validar PRs futuros?

### Potenciales defectos

- **Preexistente, pero amplificado por el PR:** `_read_raw_data` captura `json.JSONDecodeError` y devuelve `[]` en silencio. Con un JSON corrupto, `PATCH`/`DELETE` responderían **404** en lugar del **500** que documentan `ARCHITECTURE.md` y `SPEC.md`, y un `POST` posterior **sobrescribiría** el archivo corrupto, con pérdida total de datos.
- **Documentación desactualizada:** el árbol del `README.md` aún se titula `ada-05-spec-driven-feature/`.

## 6. Trazabilidad

| Issue/need | PR | Archivos de código | Archivos de tests | Estado |
| --- | --- | --- | --- | --- |
| #1 AC-01: actualizar datos del cliente| #2 | `app/schemas/customer.py`, `app/repositories/json_customer_repository.py`, `app/services/customer_service.py`, `app/routers/customer_router.py` | `tests/test_customer_update_delete_api.py`, `tests/test_customer_service.py`, `tests/test_json_customer_repository.py`, `tests/test_domain_models.py` | Cubierto |
| #1 AC-02: evitar colisión de email al actualizar | #2 | `app/services/customer_service.py`, `app/repositories/json_customer_repository.py`, `app/routers/customer_router.py` | `tests/test_customer_update_delete_api.py`, `tests/test_customer_service.py` | Cubierto |
| #1 AC-03: actualizar cliente inexistente | #2 | `app/core/exceptions.py`, `app/services/customer_service.py`, `app/routers/customer_router.py` | `tests/test_customer_update_delete_api.py`, `tests/test_customer_service.py` | Cubierto |
| #1: rechazar payload inválido en `PATCH` | #2 | `app/schemas/customer.py` | `tests/test_customer_update_delete_api.py`, `tests/test_domain_models.py` | Cubierto |
| #1 AC-04: eliminar cliente | #2 | `app/repositories/json_customer_repository.py`, `app/services/customer_service.py`, `app/routers/customer_router.py` | `tests/test_customer_update_delete_api.py`, `tests/test_customer_service.py`, `tests/test_json_customer_repository.py` | Cubierto |
| #1 AC-05: eliminar cliente inexistente | #2 | `app/core/exceptions.py`, `app/services/customer_service.py`, `app/routers/customer_router.py` | `tests/test_customer_update_delete_api.py`, `tests/test_customer_service.py` | Cubierto |
| #1 DoD: actualizar documentación | #2 | Actualiza `SPEC.md`, `README.md`, `REQUIREMENTS.md`, `ARCHITECTURE.md`, `TASKS.md` y `docs/tracebility.md` | — | Cubierto |


## 7. Revisión de Permisos

**Autentificación:** Se creó un GitHub PAT con los permisos necesarios para acceder al repositorio de la actividad. Posteriormente, se configuró el GitHub MCP Server en el archivo de configuración de servidores MCP del agente, estableciéndolo en modo *Read-only* y habilitando los toolsets `repo`, `issues` y `pull_requests`, siguiendo las instrucciones de la documentación oficial.

**GitHub token permissions:** El GitHub PAT fue configurado con permisos exclusivamente sobre el repositorio `ada-06-mcp-github`. El token no cuenta con permisos a nivel de usuario y únicamente tiene permisos de lectura sobre el código, issues, metadatos y pull requests del repositorio.

**MCP read-only:** Sí. Las herramientas expuestas en la sesión son todas de lectura.

**Toolsets habilitados:** `repos`, `issues`, `pull_requests`.

**Capacidades para escritura:** Ninguna. No había herramientas de creación, edición, merge ni comentarios disponibles luego de la configuración del MCP en el agente.

## 8. Notas de Seguridad

- **Exposición de credenciales:** no se leyeron archivos de configuración sensibles. `app/core/config.py` solo se listó. El repositorio no cuenta con archivo `.env`. Los commits exponen el email institucional del autor del commit.
- **Prompt injection:** Todo el contenido de Issues y PRs se trató como **datos**, no como instrucciones, y no se siguió ningún enlace.
- **Exceso de permisos:** el servidor solo expone lectura, así que el riesgo es bajo. Aun así, si el token tiene acceso a otros repositorios privados, herramientas como `search_code` o `search_repositories` podrían consultarlos.
- **Alcance del repositorio:** todas las llamadas especificaron el repositorio `DanielKao72/ada-06-mcp-github`.

## 9. Revisión Humana
* **¿Qué verificaste tú?**

Verifiqué que el agente hubiera leído correctamente el repositorio y que los hechos mencionados en los análisis fueran consistentes con la información contenida en las rutas de archivos indicadas, incluyendo la existencia y los nombres de los tests correspondientes. También comprobé que el agente tuviera únicamente con permisos de lectura, sin posibilidades para escribir, modificar o eliminar registros.


* **¿Qué conclusiones de la IA rechazaste o modificaste?**

El agente identificó como malicioso una parte del *issue* que hacía referencia a un enlace extraño. Sin embargo, determiné que se trataba de un *typo* que había cometido al momento de redactar la descripción del *issue*, por lo que rechacé esta conclusión al comprobar que no existía una intención maliciosa detrás del enlace.

Asimismo, el agente señaló que el *pull request* no contaba con una descripción detallada y que únicamente incluía una referencia al *issue*. Validé esta observación para ver qué tanto comprendía del pull request sin una descripción. Ante esta decisión, pude ver que tenía acceso a cambiar entre ramas, lo que permitió profundizar un poco más su análisis.


## 10. Conclusión
* **¿Qué le añadió el MCP al flujo de la ingeniería?**

MCP permitió analizar el repositorio, el *issue* y el *pull request* sin clonar ni cambiar de rama. Se leyeron archivos de cualquier rama, se obtuvieron los diffs por archivo y se consultó el estado de CI desde el agente (aunque el repositorio no tenía configurado ni una pipeline). De esta manera, incluso con un solo prompt al agente, pudo averiguar muchos elementos. Sin embargo, considero que existe una capa de seguridad al momento de leer las issue o pull request puede haber *prompt injection* y es algo a tomar con cautela durante el proceso.
