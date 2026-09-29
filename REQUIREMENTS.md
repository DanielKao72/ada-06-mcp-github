# Requirements — Customer Search

## User Story
As a user, I want to search customers by name or email, so that I can quickly find the customer record I need.

As an admin, I want to update or delete an existing customer, so that I can keep customer records accurate across their full lifecycle.

## Functional Requirements

### FR-01: Partial Substring Search by Name or Email
1. **Source:** API Client / User searching for a customer
2. **Stimulus:** Submits a `GET /api/v1/customers/search?q={term}` request with a partial substring of a customer's name or email (e.g., `"joh"` or `"example.com"`)
3. **Artifact:** Customer Search Endpoint & Service
4. **Environment:** Normal operation with local JSON storage containing customer records
5. **Response:** Filters customer records where the search term is present as a substring within `name` OR `email` (case-insensitive) and returns the matching records
6. **Measure:** Returns HTTP 200 OK with a JSON array containing 100% of matching customer records and 0 non-matching records

### FR-02: Case-Insensitive Matching and Input Trimming
1. **Source:** API Client / User sending unnormalized query text
2. **Stimulus:** Submits a search query with mixed casing and leading/trailing whitespace (e.g., `"  cArLoS  "`)
3. **Artifact:** Customer Search Service & Validator
4. **Environment:** Normal operation
5. **Response:** Trims leading and trailing whitespace from the query term and performs case-insensitive matching against stored customer names and emails
6. **Measure:** Returns identical matching results for `"carlos"`, `"CARLOS"`, and `"  cArLoS  "` with HTTP 200 OK

### FR-03: Search Query Parameter Validation
1. **Source:** API Client / User sending invalid or missing search parameters
2. **Stimulus:** Submits a search request without the query parameter `q`, or with `q` having a length of less than 2 characters, greater than 100 characters, or containing only whitespace
3. **Artifact:** Customer Search Request Validator (FastAPI / Pydantic)
4. **Environment:** Normal operation
5. **Response:** Rejects the request prior to data querying and provides clear validation error details
6. **Measure:** Returns HTTP 422 Unprocessable Entity with a validation error payload explaining parameter constraint violations in 100% of invalid request cases

### FR-04: No Matching Results Handling
1. **Source:** API Client / User searching for non-existent records
2. **Stimulus:** Submits a valid search query `q` that does not match any existing customer's name or email
3. **Artifact:** Customer Search Endpoint & Service
4. **Environment:** Normal operation with empty or populated local JSON storage
5. **Response:** Processes the query successfully and returns an empty collection without errors
6. **Measure:** Returns HTTP 200 OK with an empty JSON array `[]` in the response body

### FR-05: Customer Creation and Persistence
1. **Source:** API Client / Admin creating a new customer
2. **Stimulus:** Submits a `POST /api/v1/customers` request with a valid `name` and `email` JSON payload
3. **Artifact:** Customer Creation Endpoint & JSON Repository
4. **Environment:** Normal operation with read/write access to the local JSON file
5. **Response:** Validates email format, generates a unique UUID `id` and an ISO UTC `created_at` timestamp, appends the customer record into the local JSON file, and returns the created customer
6. **Measure:** Returns HTTP 201 Created with the persisted customer JSON object containing valid `id`, `name`, `email`, and `created_at` fields; new record is immediately queryable

### FR-06: List All Customers
1. **Source:** API Client / Admin requesting the full customer directory
2. **Stimulus:** Submits a `GET /api/v1/customers` request
3. **Artifact:** Customer Retrieval Endpoint & JSON Repository
4. **Environment:** Normal operation
5. **Response:** Reads and deserializes all customer records stored in the local JSON file
6. **Measure:** Returns HTTP 200 OK with a JSON array containing all persisted customer records (or `[]` if storage is empty)

### FR-07: Partial Customer Update
1. **Source:** API Client / Admin maintaining customer records
2. **Stimulus:** Submits a `PATCH /api/v1/customers/{customer_id}` request with a JSON payload containing `name`, `email`, or both
3. **Artifact:** Customer Update Endpoint, Customer Service & JSON Repository
4. **Environment:** Normal operation with read/write access to the local JSON file
5. **Response:** Validates the payload, verifies the customer exists and that a new email is not used by another customer, applies only the provided fields, keeps `id` and `created_at` immutable, and persists the updated record
6. **Measure:** Returns HTTP 200 OK with the updated customer; HTTP 404 Not Found if `customer_id` does not exist; HTTP 409 Conflict if the email belongs to another customer; HTTP 422 Unprocessable Entity if the payload fails validation. Rejected requests leave storage unchanged

### FR-08: Customer Deletion
1. **Source:** API Client / Admin maintaining customer records
2. **Stimulus:** Submits a `DELETE /api/v1/customers/{customer_id}` request
3. **Artifact:** Customer Deletion Endpoint, Customer Service & JSON Repository
4. **Environment:** Normal operation with read/write access to the local JSON file
5. **Response:** Permanently removes the matching customer record from the local JSON file
6. **Measure:** Returns HTTP 204 No Content with an empty body on success; HTTP 404 Not Found if `customer_id` does not exist in storage

## Non-Functional Requirements
* **NFR-01 (Local JSON Persistence):** Data persistence must rely exclusively on a local JSON file (e.g., `data/customers.json`), with safe read/write operations and automatic file initialization if missing.
* **NFR-02 (Decoupled Architecture & Testability):** The application architecture must decouple the HTTP presentation layer (FastAPI), business logic (Service), and data access layer (JSON Repository), facilitating dependency injection for isolated testing.
* **NFR-03 (Automated Testing & Code Quality):** Comprehensive test coverage using `pytest` and `httpx` (`TestClient`), leveraging isolated temporary JSON file fixtures (`tmp_path`) for unit and integration testing.

## Open Questions
* **Q-01:** Will pagination (`limit`, `offset`) and sorting support be required if customer volume expands?
* **Q-02:** Should duplicate email addresses be strictly prohibited when registering new customers in the JSON store?

## Constraints / Assumptions
* **C-01:** Technology stack constrained to Python 3.10+, FastAPI framework, local JSON file persistence (no external SQL/NoSQL databases), and pytest testing suite.
* **A-01:** Customer volume in the JSON store is assumed to be moderate, suitable for in-memory deserialization and filtering per request.