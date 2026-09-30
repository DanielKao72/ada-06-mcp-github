# ADA-06 — GitHub MCP Server

Actividad de aprendizaje para configurar, probar y analizar la conexión de un agente de IA con GitHub mediante el **GitHub MCP Server**, en modo de solo lectura, sobre el repositorio `DanielKao72/ada-06-mcp-github`.

## Entregables

| Archivo | Contenido |
| --- | --- |
| `docs/MCP_GITHUB_TOOL_INVENTORY.md` | Inventario de las herramientas expuestas por el MCP, su uso en la ADA y su riesgo |
| `docs/MCP_GITHUB_PERMISSION_REVIEW.md` | Revisión de permisos (capacidad, necesidad, control y decisión) y análisis de seguridad |
| `results/github-mcp-review.md` | Análisis de ingeniería del repositorio, del Issue #1 y del PR #2 |
| `AI_USAGE_LOG.md` | Bitácora del uso de IA y de la validación humana en cada etapa |

## Reflexión

### 1. ¿Qué información obtuvo el agente mediante MCP que normalmente habrías tenido que copiar al prompt?

- La estructura de directorios del repositorio.
- El contenido de `README.md`, `ARCHITECTURE.md`, `requirements.txt`, `app/main.py`, `app/dependencies.py`, `tests/conftest.py` y el repositorio JSON.
- Las ramas y el historial de commits.
- El cuerpo completo del Issue #1 con sus criterios de aceptación.
- Los metadatos del PR #2 y el diff de sus 15 archivos modificados.

Sin MCP habría tenido que copiar y pegar cada archivo; o bien, darle el suficiente contexto de los cambios hechos en el PR y qué issue resolvía.

### 2. ¿Cuál es la diferencia entre el GitHub MCP Server y una GitHub Tool?

El **GitHub MCP Server** es el servicio que implementa MCP. Existe un proceso para configurar el agente de IA para conectarse a este servicio (se autentica con GitHub mediante el PAT y le ofrece al agente un catálogo de herramientas agrupadas en toolsets). Una **GitHub Tool** es una sola operación dentro del servicio del MCP Server, con un nombre, parámetros definidos y una acción concreta sobre la API de GitHub; por ejemplo, `issue_read` o `get_file_contents`.

### 3. ¿Qué toolset fue necesario para leer código? ¿Cuál para Issues? ¿Cuál para PRs?

| Necesidad | Toolset | Herramientas usadas |
| --- | --- | --- |
| Leer código | `repos` | `get_file_contents`, `list_branches`, `list_commits` |
| Issues | `issues` | `list_issues`, `issue_read` |
| Pull requests | `pull_requests` | `list_pull_requests`, `pull_request_read` |

### 4. ¿Qué diferencia existe entre permisos del PAT y herramientas expuestas por MCP?

- Los **permisos del PAT** tiene un alcance hasta GitHub. Crea un token que le dice a GitHub sobre qué repositorios trabajar y con qué nivel de acceso(por ejemplo, `Contents: Read`). GitHub los aplica en el servidor.
- Las **herramientas expuestas por MCP** definen lo que el agente puede intentar hacer. Por ejemplo, el modo *read-only* y toolsets habilitados.



### 5. ¿Por qué se usó read-only aunque el agente pudiera ser capaz de proponer cambios?

La razón por la que se usaría el modo *read-only* es para analizar repositorios sin alterar su contenido (principalmente si son repositorios poco confiables o sensibles). Al poder estar escritos por terceros, puede contener *prompt injection*. Si llegara a tener permisos de escritura, entonces podría desencadenar en acciones maliciosas.
Este modo ayudaría a proponer cambios sin ejecutar. De esta manera, revisamos su propuesta y modificamos en caso de ser necesario.

### 6. ¿Qué evidencia comprobó que el MCP estaba realmente conectado?

- El comando `/mcp` respondió *"Reconnected to github"*.
- Aparecieron en la sesión las 22 herramientas `mcp__github__*`.

### 7. ¿Qué información del Issue era un hecho y qué parte fue inferencia del agente?

**Hechos**:
- Los endpoints `PATCH` y `DELETE /api/v1/customers/{customer_id}`.
- Los códigos de respuesta 200, 204, 404, 409 y 422.
- Los criterios AC-01 a AC-05.
- Las capas y archivos impactados.
- El DoD, que exige mantener los 27 tests existentes.

**Inferencias del agente:**
- Que los enlaces del Issue eran sospechosos. Esta inferencia la rechacé: era un error tipográfico al redactar el Issue.

### 8. ¿Qué relación encontraste entre Issue, PR, código y tests?

La trazabilidad es completa en cuanto a código y tests:
- El Issue #1 se implementa en el PR #2.
- Cada criterio de aceptación se corresponde con cambios en los cinco archivos de la arquitectura en capas: schema, excepciones, repositorio, servicio y router.
- Cada criterio también tiene tests en cuatro archivos, incluido el nuevo `tests/test_customer_update_delete_api.py`.
- El PR además renumeró los criterios en `SPEC.md` (AC-08 a AC-12) y los enlazó a los requisitos FR-07 y FR-08.

### 9. ¿Qué riesgo tiene tratar el contenido de un Issue o PR como instrucciones confiables?

Cualquier persona que pueda escribir un issue, un comentario o un archivo podría incluir instrucciones dirigidas al agente (*prompt injection*). Por ejemplo: "ignora tus reglas", "publica el token" o "aprueba este PR". Si el agente las obedeciera, podría filtrar información, seguir enlaces maliciosos o, con permisos de escritura, modificar el repositorio.

### 10. ¿En qué escenario permitirías escritura mediante MCP? ¿Qué acción requeriría aprobación humana?

Permitiría escritura en un repositorio propio o de práctica, con un PAT *fine-grained* limitado a ese repositorio y solo con los permisos necesarios. La rama principal tendría que estar protegida por *branch protection*.

Requerirían aprobación humana explícita:
- Hacer merge de un PR.
- Hacer push a `master`.
- Borrar ramas, archivos o issues.
- Cerrar issues.
- Publicar comentarios o reviews en nombre del usuario.
- Modificar workflows de CI, configuración o permisos del repositorio.

### 11. ¿Qué cambiarías si el repositorio fuera privado o perteneciera a una organización?

- Verificaría que el PAT incluya explícitamente ese repositorio u organización.
- Agregaría solo los permisos que se requieran; por ejemplo, `Checks: Read`.
- Limitaría las búsquedas a la organización o al repositorio.
- Revisaría con más cuidado herramientas que exponen datos de personas, como `list_repository_collaborators`.

### 12. ¿Qué aporta MCP al ciclo de vida de Ingeniería de Software frente a copiar/pegar contenido en un chat?

MCP le da al agente acceso directo, actualizado y trazable a los artefactos reales del proyecto: código de cualquier rama, issues, PRs, diffs y estado de CI. Esto reduce errores por contexto incompleto o desactualizado y permite revisiones más completas en menos tiempo (con un solo prompt puede tener una idea muy clara del proyecto).
