# Revisión de permisos del MCP server de GitHub

| Capacidad | ¿Necesario? | ¿Aceptado? | Control | Decisión |
| --- | --- | --- | --- | --- |
| Leer contenidos del repositorio (archivos, directorios, commits, ramas, tags, releases) | Sí | Sí | PAT `Contents: Read` | Keep |
| Leer metadatos del repositorio | Sí | Sí | PAT `Metadata: Read`, obligatorio en todo PAT fine-grained | Keep |
| Leer issues, comentarios y etiquetas | Sí | Sí | PAT `Issues: Read` + toolset `issues` | Keep |
| Leer pull requests (detalle, diff, archivos, reviews y comentarios) | Sí | Sí | PAT `Pull requests: Read` + toolset `pull_requests` | Keep |
| Listar colaboradores del repositorio | No | Sí | PAT `Metadata: Read` y acceso del dueño del repositorio; solo expone usuarios y roles | Keep |
| Búsquedas (`search_code`, `search_repositories`, `search_issues`, `search_pull_requests`, `search_commits`) | No | Sí, con restricción | PAT limitado a *Only select repositories*; consultas exclsuivas a `repo:DanielKao72/ada-06-mcp-github`; | Restrict |
| Acceso a otros repositorios del usuario u organización | No | No | PAT con *Only select repositories* (un solo repositorio) | Deny |
| Crear o editar issues y comentarios | No | No | PAT sin `Issues: Write` + MCP en modo *read-only* | Deny |
| Crear, comentar, revisar o hacer merge de pull requests | No | No | PAT sin `Pull requests: Write` + MCP en modo *read-only* | Deny |
| Modificar archivos, hacer push o crear/borrar ramas | No | No | PAT sin `Contents: Write` + MCP en modo *read-only* | Deny |
| Toolsets no requeridos (`actions`, `code_security`, `secret_protection`, `notifications`, `orgs`, `users`, `gists`, etc.) | No | No | Solo se habilitan los toolsets `repos`, `issues` y `pull_requests` | Deny |

# Análisis de seguridad

| Riesgo | Ejemplo | Mitigación |
| --- | --- | --- |
| *Prompt injection* | Un issue, PR, comentario o archivo contiene instrucciones maliciosas dirigidas al agente. | Tratar el contenido de GitHub como datos no confiables, nunca como instrucciones; mantener el MCP en *read-only*. |
| Enlaces o recursos externos no confiables | El cuerpo del Issue #1 incluía enlaces sospechosos que el agente podría intentar abrir. | No seguir enlaces que vengan de issues o PRs; limitar el análisis al contenido del repositorio. |
| Filtración del PAT | El token queda en texto plano en el archivo de configuración del MCP y ese archivo se sube al repositorio o aparece en la conversación. | Guardar el PAT en una variable de entorno o en un gestor de secretos; no versionar la configuración que lo contiene; definir expiración y revocarlo al terminar la tarea. |
| Exceso de permisos del token | Un PAT *classic* con scope `repo` daría lectura y escritura sobre **todos** los repositorios del usuario. | Usar un PAT *fine-grained*, limitado a un solo repositorio y con permisos solo de lectura. |
| Alcance fuera del repositorio | `search_code` o `search_repositories` sin el calificador `repo:` devuelven resultados de otros repositorios, incluidos privados si el token tiene acceso. | Limitar el PAT a *Only select repositories*; acotar cada consulta con `repo:DanielKao72/ada-06-mcp-github`. |
| Exposición de secretos del repositorio | `get_file_contents` o `get_commit` leen un `.env` o una credencial que se commiteó por error, y su contenido termina en la conversación o en un reporte. | No leer archivos de configuración sensibles; mantener `.env` en `.gitignore`. |
| Exposición de datos personales | `list_commits` y `list_repository_collaborators` devuelven emails y usuarios de los autores y colaboradores. | Consultar solo lo necesario; no copiar emails a los reportes. |
