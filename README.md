# Customer Search Service

A lightweight, RESTful microservice built with **FastAPI** and **Pydantic** to search and manage customer records using a local **JSON file** for data persistence.

---

## Features

- **Partial Substring Search:** Query customers by partial name or email matching (e.g., prefix, infix, suffix).
- **Case-Insensitive & Whitespace Trimming:** Search terms are automatically trimmed and matched regardless of uppercase/lowercase input.
- **Strict Input Validation:** Enforces query length limits ($2 \le \text{length} \le 100$) and RFC-compliant email formats via Pydantic.
- **Local JSON File Persistence:** Zero external database dependencies; automatically creates and persists customer records to `data/customers.json`.
- **Comprehensive Automated Testing:** 100% test coverage using `pytest` and `httpx` with isolated temporary filesystem fixtures (`tmp_path`).

---

## Project Structure

```
ada-05-spec-driven-feature/
├── app/
│   ├── core/
│   │   ├── config.py                   # Application settings & data paths
│   │   └── exceptions.py               # Domain-specific exceptions
│   ├── schemas/
│   │   └── customer.py                 # Pydantic validation and response schemas
│   ├── repositories/
│   │   └── json_customer_repository.py # Local JSON file I/O and filtering
│   ├── services/
│   │   └── customer_service.py         # Business logic and query normalization
│   ├── routers/
│   │   └── customer_router.py          # FastAPI route handlers & endpoints
│   ├── dependencies.py                 # Dependency injection providers
│   └── main.py                         # Application factory & entrypoint
├── data/
│   └── customers.json                  # Local JSON data store (created at runtime)
├── tests/
│   ├── conftest.py                     # Pytest fixtures & isolated TestClient
│   ├── test_domain_models.py           # Unit tests for domain models & validation
│   ├── test_json_customer_repository.py# Unit tests for repository layer
│   ├── test_customer_service.py        # Unit tests for service layer
│   ├── test_customer_api_validation.py # Integration tests for status codes & errors
│   └── test_customer_search_api.py     # End-to-end acceptance & search scenario tests
├── requirements.txt                    # Project dependencies
├── REQUIREMENTS.md                     # Functional & non-functional requirements
├── SPEC.md                             # Feature specification & acceptance criteria
├── ARCHITECTURE.md                     # Architectural design & data flow diagrams
├── TASKS.md                            # Task breakdown & progress tracking
└── README.md                           # Documentation & quickstart guide
```

---

## Getting Started

### 1. Prerequisites
- **Python 3.10+** (Python 3.11 recommended)
- **pip** package manager

### 2. Installation
Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Running the API Server
Start the development server with Uvicorn:

```bash
uvicorn app.main:app --reload --port 8000
```

The interactive API documentation will be available at:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Running the Test Suite

Run the full automated test suite using `pytest`:

```bash
pytest -v
```

To run with coverage or concise output:

```bash
pytest
```

---

## API Reference & Examples

### 1. Health Check
Checks if the service is running.

- **Endpoint:** `GET /health`
- **Request:**
  ```bash
  curl -X GET http://127.0.0.1:8000/health
  ```
- **Response (HTTP 200 OK):**
  ```json
  {
    "status": "healthy",
    "version": "1.0.0"
  }
  ```

---

### 2. Create Customer
Registers a new customer record with a unique UUID and UTC timestamp.

- **Endpoint:** `POST /api/v1/customers`
- **Request:**
  ```bash
  curl -X POST http://127.0.0.1:8000/api/v1/customers \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Alexander Hamilton",
      "email": "hamilton@treasury.gov"
    }'
  ```
- **Response (HTTP 201 Created):**
  ```json
  {
    "id": "f8455716-bb9d-4181-bc4f-baa0b176633c",
    "name": "Alexander Hamilton",
    "email": "hamilton@treasury.gov",
    "created_at": "2026-09-23T23:40:00.000000+00:00"
  }
  ```
- **Duplicate Email Conflict (HTTP 409 Conflict):**
  ```json
  {
    "detail": "Customer with email 'hamilton@treasury.gov' already exists."
  }
  ```

---

### 3. Search Customers
Performs a case-insensitive substring search across customer names and emails.

- **Endpoint:** `GET /api/v1/customers/search?q={query}`
- **Query Parameter:** `q` (required, 2 to 100 characters)

#### Search by Partial Name:
- **Request:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/api/v1/customers/search?q=alex"
  ```
- **Response (HTTP 200 OK):**
  ```json
  [
    {
      "id": "f8455716-bb9d-4181-bc4f-baa0b176633c",
      "name": "Alexander Hamilton",
      "email": "hamilton@treasury.gov",
      "created_at": "2026-09-23T23:40:00.000000+00:00"
    }
  ]
  ```

#### Search by Partial Email Domain:
- **Request:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/api/v1/customers/search?q=treasury"
  ```
- **Response (HTTP 200 OK):**
  ```json
  [
    {
      "id": "f8455716-bb9d-4181-bc4f-baa0b176633c",
      "name": "Alexander Hamilton",
      "email": "hamilton@treasury.gov",
      "created_at": "2026-09-23T23:40:00.000000+00:00"
    }
  ]
  ```

#### Non-Matching Search:
- **Request:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/api/v1/customers/search?q=nonexistent"
  ```
- **Response (HTTP 200 OK):**
  ```json
  []
  ```

#### Validation Error (Parameter too short):
- **Request:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/api/v1/customers/search?q=a"
  ```
- **Response (HTTP 422 Unprocessable Entity):**
  ```json
  {
    "detail": [
      {
        "type": "string_too_short",
        "loc": ["query", "q"],
        "msg": "String should have at least 2 characters",
        "input": "a",
        "ctx": {"min_length": 2}
      }
    ]
  }
  ```

---

### 4. List All Customers
Retrieves all customer records currently persisted in the JSON store.

- **Endpoint:** `GET /api/v1/customers`
- **Request:**
  ```bash
  curl -X GET http://127.0.0.1:8000/api/v1/customers
  ```
- **Response (HTTP 200 OK):**
  ```json
  [
    {
      "id": "f8455716-bb9d-4181-bc4f-baa0b176633c",
      "name": "Alexander Hamilton",
      "email": "hamilton@treasury.gov",
      "created_at": "2026-09-23T23:40:00.000000+00:00"
    }
  ]
  ```
