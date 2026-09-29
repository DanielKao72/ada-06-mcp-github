# Customer Search Feature Specification

## Goal
Provide a lightweight, RESTful customer search capability that allows clients to locate customer records via partial name or email matching, backed by local JSON persistence, robust input validation, and comprehensive automated test coverage.

## Requirements Covered
- `FR-01`: Partial Substring Search by Name or Email
- `FR-02`: Case-Insensitive Matching and Input Trimming
- `FR-03`: Search Query Parameter Validation
- `FR-04`: No Matching Results Handling
- `FR-05`: Customer Creation and Persistence
- `FR-06`: List All Customers
- `FR-07`: Partial Customer Update
- `FR-08`: Customer Deletion
- `NFR-01`: Local JSON Persistence
- `NFR-02`: Decoupled Architecture & Testability
- `NFR-03`: Automated Testing & Code Quality

## Scope
* **Customer Search Endpoint (`GET /api/v1/customers/search?q={term}`):** Substring matching against customer name and email.
* **Input Normalization & Validation:** Trimming whitespace, case-insensitivity, and length validation ($2 \le \text{length} \le 100$).
* **Customer Management Endpoints:**
  * `POST /api/v1/customers`: Register customer with unique UUID, RFC-compliant email, name, and UTC timestamp.
  * `GET /api/v1/customers`: Retrieve all registered customer records.
  * `PATCH /api/v1/customers/{customer_id}`: Partially update a customer's `name` and/or `email`.
  * `DELETE /api/v1/customers/{customer_id}`: Permanently delete a customer record.
* **Local File Persistence:** Reading, writing, and automatically initializing the local JSON data store (`data/customers.json`).
* **Automated Testing Suite:** End-to-end endpoint tests and unit tests using `pytest` and `httpx` (`TestClient`) with isolated temporary file fixtures (`tmp_path`).

## Out of Scope
* Integration with external database management systems (e.g., PostgreSQL, MySQL, MongoDB).
* Full-text search engine indexing (e.g., Elasticsearch, Meilisearch).
* Full customer replacement (`PUT`) and bulk update/delete operations.
* Soft deletion, deletion history, or restoring deleted customers.
* Retrieving a single customer by ID (`GET /api/v1/customers/{customer_id}`).
* User authentication, authorization, and rate limiting.
* Fuzzy matching algorithms (e.g., Levenshtein distance, Soundex).

## Domain Model

### Entity: `Customer`
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | `str` (UUIDv4) | Yes | Unique identifier generated upon creation |
| `name` | `str` | Yes | Customer full name (1 to 150 characters) |
| `email` | `str` (EmailStr) | Yes | Valid RFC-compliant email address |
| `created_at` | `str` (ISO 8601 UTC) | Yes | Creation timestamp in UTC (e.g., `2026-09-23T23:40:00Z`) |

### JSON Data Storage Format
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "created_at": "2026-09-23T23:40:00Z"
  }
]
```

## Search Rules
1. **Substring Match Condition:** A customer record matches if the normalized search query is a substring of `customer.name` OR a substring of `customer.email`.
2. **Case-Insensitivity:** Comparisons are evaluated using lowercase representations (`query.lower() in field.lower()`).
3. **Query Trimming:** Leading and trailing whitespaces in the search query parameter are stripped prior to evaluation.
4. **Empty Match Set:** If no customer records satisfy the substring condition, the service returns an empty list `[]` with HTTP status `200 OK`.
5. **Full Match Return:** All matching records are returned in the response array.

## Validation Rules

### 1. Search Query (`q`)
* Parameter is required in `GET /api/v1/customers/search`.
* Length after trimming must be $\ge 2$ characters.
* Length must be $\le 100$ characters.
* If validation fails, response must be HTTP `422 Unprocessable Entity`.

### 2. Customer Creation Payload (`POST /api/v1/customers`)
* `name`: Required, non-empty string, maximum 150 characters.
* `email`: Required, must be a valid email format conforming to standard email syntax.
* Duplicate email check: Returns HTTP `409 Conflict` or `422 Unprocessable Entity` if the email already exists in storage.

### 3. Customer Update Payload (`PATCH /api/v1/customers/{customer_id}`)
* At least one of `name` or `email` must be provided; an empty body `{}` is rejected with `422`.
* `name` (optional): Same rules as creation — non-empty after trimming, maximum 150 characters.
* `email` (optional): Must be a valid email format conforming to standard email syntax.
* Explicit `null` values for `name` or `email` are rejected with `422`.
* `id` and `created_at` are immutable: including them (or any other unknown field) in the payload is rejected with `422`.
* Only the provided fields are modified; omitted fields keep their stored values.
* Duplicate email check: If the new email (case-insensitive) belongs to **another** customer, returns HTTP `409 Conflict`. Re-submitting the customer's own current email is allowed.
* Unknown `customer_id`: returns HTTP `404 Not Found`.

### 4. Customer Deletion (`DELETE /api/v1/customers/{customer_id}`)
* On success the record is permanently removed from `data/customers.json` and the response is HTTP `204 No Content` with an empty body.
* Unknown `customer_id`: returns HTTP `404 Not Found`.

## Error Handling
* **HTTP 422 Unprocessable Entity:** Returned when request parameters or payload fail Pydantic schema validation (e.g., missing parameter `q`, search term shorter than 2 characters, invalid email format, empty or immutable-field update payloads).
* **HTTP 404 Not Found:** Returned when updating or deleting a `customer_id` that does not exist in storage.
* **HTTP 409 Conflict:** Returned when attempting to create a customer with an email that is already registered, or to update a customer's email to one owned by another customer.
* **HTTP 500 Internal Server Error:** Returned in the event of unexpected file I/O errors or corrupted JSON data, accompanied by descriptive server-side logging.

## Acceptance Criteria

### AC-01: Search by Partial Name
* **Given** stored customers "Alice Johnson" and "Bob Smith",
* **When** a client requests `GET /api/v1/customers/search?q=lice`,
* **Then** the API responds with HTTP 200 OK and a list containing "Alice Johnson".

### AC-02: Search by Partial Email
* **Given** a stored customer with email "support@acme-corp.com",
* **When** a client requests `GET /api/v1/customers/search?q=acme`,
* **Then** the API responds with HTTP 200 OK and a list containing the matching customer record.

### AC-03: Case-Insensitive Search with Whitespace
* **Given** a stored customer "Carlos Gomez" (`carlos@domain.com`),
* **When** a client requests `GET /api/v1/customers/search?q=%20%20CARLOS%20%20`,
* **Then** the API responds with HTTP 200 OK and returns "Carlos Gomez".

### AC-04: Reject Search Query Violations
* **Given** the search API endpoint,
* **When** a client requests `GET /api/v1/customers/search?q=a` (less than 2 characters) or omits `q`,
* **Then** the API responds with HTTP 422 Unprocessable Entity.

### AC-05: Non-Matching Query Returns Empty List
* **Given** a customer database with existing records,
* **When** a client requests `GET /api/v1/customers/search?q=nonexistentterm`,
* **Then** the API responds with HTTP 200 OK and response body `[]`.

### AC-06: Create Customer and Persist to JSON
* **Given** a valid payload `{"name": "Diana Prince", "email": "diana@themyscira.gov"}`,
* **When** a client requests `POST /api/v1/customers`,
* **Then** the API responds with HTTP 201 Created containing generated `id` and `created_at`, and the customer is retrievable from the JSON store.

### AC-07: List All Registered Customers
* **Given** multiple customer records stored in `customers.json`,
* **When** a client requests `GET /api/v1/customers`,
* **Then** the API responds with HTTP 200 OK containing all stored customer records.

### AC-08: Successfully Update Customer Details
* **Given** an existing customer with ID `cust-123` ("John Doe", "john@example.com"),
* **When** a client sends `PATCH /api/v1/customers/cust-123` with `{"name": "Johnathan Doe"}`,
* **Then** the service updates the record in JSON storage
* **And** returns HTTP 200 OK with the updated name and unchanged email, `id`, and `created_at`.

### AC-09: Prevent Email Collision on Update
* **Given** customer A ("a@domain.com") and customer B ("b@domain.com"),
* **When** a client sends `PATCH` on customer B with `{"email": "a@domain.com"}`,
* **Then** the service rejects the operation
* **And** returns HTTP 409 Conflict.

### AC-10: Update Non-Existent Customer
* **Given** an empty or populated customer store,
* **When** a client sends `PATCH /api/v1/customers/non-existent-id`,
* **Then** the service returns HTTP 404 Not Found.

### AC-11: Successfully Delete Customer
* **Given** an existing customer with ID `cust-123`,
* **When** a client sends `DELETE /api/v1/customers/cust-123`,
* **Then** the record is permanently removed from the JSON store
* **And** the service returns HTTP 204 No Content.

### AC-12: Delete Non-Existent Customer
* **Given** a customer ID `non-existent-id` not present in storage,
* **When** a client sends `DELETE /api/v1/customers/non-existent-id`,
* **Then** the service returns HTTP 404 Not Found.

## Test Scenarios
* **TS-01 (Partial Name Search):** Verify search matches prefix, infix, and suffix substrings in customer names.
* **TS-02 (Partial Email Search):** Verify search matches username, separator, domain, and TLD substrings.
* **TS-03 (Case Insensitivity):** Verify queries in lowercase, uppercase, and mixed casing return identical result sets.
* **TS-04 (Whitespace Handling):** Verify queries with leading, trailing, and padded spaces are trimmed and processed correctly.
* **TS-05 (Boundary & Validation Testing):** Test query string bounds ($0$ chars / missing $\rightarrow 422$, $1$ char $\rightarrow 422$, $2$ chars $\rightarrow 200$, $100$ chars $\rightarrow 200$, $101$ chars $\rightarrow 422$).
* **TS-06 (No Matching Results):** Verify valid queries with no matching records cleanly return `[]` with status 200.
* **TS-07 (Customer Creation):** Verify `POST /api/v1/customers` creates records with valid UUIDs, timestamps, and persists data to disk.
* **TS-08 (Duplicate Email Prevention):** Verify attempting to create a customer with an existing email returns an appropriate client error.
* **TS-09 (Full Listing):** Verify `GET /api/v1/customers` returns all entries from storage.
* **TS-10 (Repository Initialization & Isolation):** Verify repository creates JSON file when absent and works reliably with `pytest`'s `tmp_path` fixture.
* **TS-11 (Partial Update):** Verify `PATCH` updates only the provided fields (`name`, `email`, or both), persists them, and preserves `id` and `created_at`.
* **TS-12 (Update Email Collision):** Verify updating to another customer's email (case-insensitive) returns `409` without modifying storage, while re-submitting the customer's own email returns `200`.
* **TS-13 (Update Validation):** Verify empty body, empty/whitespace/too-long name, malformed email, explicit `null`, and immutable/unknown fields return `422` without modifying storage.
* **TS-14 (Update Not Found):** Verify `PATCH` on an unknown ID returns `404` for both empty and populated stores.
* **TS-15 (Deletion):** Verify `DELETE` removes only the targeted record from disk and returns `204` with an empty body.
* **TS-16 (Delete Not Found):** Verify `DELETE` on an unknown or already-deleted ID returns `404` and leaves storage unchanged.

## Constraints
* **Runtime & Framework:** Python 3.10+, FastAPI, Uvicorn.
* **Schema Validation:** Pydantic v2 (including email validation via `pydantic[email]`).
* **Persistence:** Local JSON file persistence only; no SQL/NoSQL external services.
* **Testing:** `pytest` test suite with `httpx` `TestClient` and temporary filesystem fixtures (`tmp_path`).

## Open Questions
* **Q-01 (Pagination & Sorting):** N/A for initial release. Justification: In-memory filtering over local JSON is performant for expected dataset sizes; pagination will be addressed in future milestones if datasets grow.
* **Q-02 (Email Uniqueness Enforcement):** Enforced during customer creation (`POST /api/v1/customers`) and customer update (`PATCH /api/v1/customers/{customer_id}`) to avoid duplicate profiles sharing the same email in the local JSON repository.
