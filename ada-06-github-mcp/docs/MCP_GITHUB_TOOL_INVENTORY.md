# Inventario de herramientas del MCP server de GitHub

## Toolset `repos`

| Tool/Capacidad | Read/Write | Uso en el ADA | Riesgo |
| --- | --- | --- | --- |
| `get_commit` | Read | Consultar el detalle de un commit (autor, mensaje y archivos modificados) para analizar cambios del repositorio. | Medio: entre los archivos modificados puede haber información sensible. |
| `get_file_contents` | Read | Leer archivos o listar directorios del repositorio sin clonarlo. | Medio: podría leer archivos con configuración sensible; o bien, entre los archivos puede haber instrucciones maliciosas (*prompt injection*). |
| `get_latest_release` | Read | Verificar cuál es la última versión publicada del repositorio. | Bajo: es información pública que no tiene datos sensibles. |
| `get_release_by_tag` | Read | Consultar las notas y assets de una release específica a partir de su tag. | Bajo: es información (metadados) de la release que de por sí es pública. |
| `get_tag` | Read | Obtener el commit al que apunta un tag para relacionar versiones con el historial. | Bajo: son solo metadatos de GitHub. |
| `list_branches` | Read | Listar las ramas del repositorio para revisar su estructura de trabajo. | Bajo: solo lista nombres de las ramas. |
| `list_commits` | Read | Revisar el historial de commits. | Bajo: lo más sensible que expone es el correo del autor del commit, pero no involucra algún peligro. |
| `list_releases` | Read | Listar las releases publicadas del repositorio. | Bajo: solo son metadatos de publicación. |
| `list_repository_collaborators` | Read | Identificar quién tiene acceso al repositorio y con qué permisos, como parte del análisis de permisos. | Bajo: solo expone correo de los colaboradores, aunque también se expone su rol. |
| `list_tags` | Read | Listar los tags del repositorio para ubicar versiones. | Bajo: son solo metadatos de git. |
| `search_code` | Read | Buscar fragmentos de código o texto en repositorios de GitHub. | Medio: puede exponer información sensible que tenga un archivo del repositorio. |
| `search_commits` | Read | Buscar commits por mensaje, autor o fecha. | Bajo: son solo metadatos de commits. |
| `search_repositories` | Read | Encontrar repositorios por nombre, usuario u organización. | Medio: si se configura el GitHub PAT para varios repositorios; puede revelar nombres y descripciones de repositorios privados, aunque no aplica para esta actividad. |

## Toolset `issues`

| Tool/Capacidad | Read/Write | Uso en el ADA | Riesgo |
| --- | --- | --- | --- |
| `get_label` | Read | Consultar una etiqueta concreta (nombre, color, descripción) del repositorio. | Bajo: son solo metadatos de configuración. |
| `issue_read` | Read | Leer el detalle de un issue, sus comentarios, sub-issues o etiquetas. | Medio: como es contenido que pueden escribir terceros, puede incluir *prompt injection* o datos sensibles. |
| `list_issue_fields` | Read | Consultar los campos personalizados de issues disponibles en una organización. | Bajo: son solo metadatos de las issues. |
| `list_issue_types` | Read | Consultar los tipos de issue definidos en una organización. | Bajo: son solo metadatos de las issues. |
| `list_issues` | Read | Listar los issues del repositorio filtrando por estado o etiquetas. | Bajo: son solo metadatos, aunque los cuerpos pueden contener texto de terceros y ser propensos a *prompt injection*. |
| `search_issues` | Read | Buscar issues por palabras clave, autor o estado. | Medio: si el GitHub PAT está configurado para varios repositorios, entonces podría devolver contenido no confiable de lo que realmente buscamos. |

## Toolset `pull requests`

| Tool/Capacidad | Read/Write | Uso en el ADA | Riesgo |
| --- | --- | --- | --- |
| `list_pull_requests` | Read | Listar los pull requests del repositorio por estado o rama. | Bajo: son solo metadatos de PRs. |
| `pull_request_read` | Read | Leer el detalle de un PR: diff, archivos cambiados, revisiones y comentarios. | Medio: entre los archivos modificados y comentarios pueden haber información sensible; o bien, puede ser propenso a *prompt injection*. |
| `search_pull_requests` | Read | Buscar pull requests por autor, estado o palabras clave. | Bajo: son solo metadatos de PRs. |
