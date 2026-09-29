# Tasks

## T-01 Project setup
- **Goal:** Establish project dependencies, environment configuration, directory layout, and settings for local JSON storage.
- **Files:**
  - `requirements.txt`
  - `app/__init__.py`
  - `app/core/__init__.py`
  - `app/core/config.py`
  - `data/.gitkeep`
- **Acceptance:**
  - `requirements.txt` defines necessary dependencies: `fastapi`, `uvicorn[standard]`, `pydantic[email]`, `pytest`, `httpx`.
  - `app/core/config.py` exposes application settings with a configurable JSON storage file path defaulting to `data/customers.json`.
  - Application directory hierarchy matches the layout specified in `ARCHITECTURE.md`.
- **Verification:** Run `python -m pip install -r requirements.txt` and verify imports with `python -c "import fastapi, pydantic, pytest, httpx"`.

## T-02 Domain model
- **Goal:** Define Pydantic models and schemas for customer entities, input validation, and API response serialization.
- **Files:**
  - `app/schemas/__init__.py`
  - `app/schemas/customer.py`
- **Acceptance:**
  - `Customer` schema defined with `id` (str/UUID), `name` (str, 1-150 chars), `email` (EmailStr), and `created_at` (str in ISO 8601 UTC format).
  - `CustomerCreate` schema defined with `name` and `email` for customer registration payload validation.
  - `CustomerResponse` schema defined for consistent API response serialization.
- **Verification:** Instantiate `CustomerCreate` with valid data, empty strings, and invalid email formats to verify Pydantic raises `ValidationError` appropriately.

## T-03 Search logic
- **Goal:** Implement the JSON file persistence repository and the core customer service with case-insensitive substring search logic and query normalization.
- **Files:**
  - `app/repositories/__init__.py`
  - `app/repositories/json_customer_repository.py`
  - `app/services/__init__.py`
  - `app/services/customer_service.py`
- **Acceptance:**
  - `JsonCustomerRepository` reads and writes customer records to the JSON file, automatically creating parent directories and initializing an empty list `[]` if the file does not exist.
  - `JsonCustomerRepository.search(term)` filters records where `term.lower()` is a substring of `customer.name.lower()` OR `customer.email.lower()`.
  - `CustomerService.search_customers(query)` normalizes queries by stripping leading/trailing whitespace before executing the search.
  - `CustomerService.create_customer(customer_in)` generates UUID and ISO UTC timestamp, validates email uniqueness, and persists the record.
- **Verification:** Execute unit tests or interactive script verifying that substring queries for both name and email return matching records and return empty lists for non-matching queries.

## T-04 Validation and errors
- **Goal:** Build the FastAPI HTTP routing layer, dependency injection providers, parameter validation, and HTTP error handlers.
- **Files:**
  - `app/dependencies.py`
  - `app/routers/__init__.py`
  - `app/routers/customer_router.py`
  - `app/main.py`
- **Acceptance:**
  - `GET /api/v1/customers/search` requires query parameter `q` with length constraint ($2 \le \text{length} \le 100$), returning `200 OK` on success and `422 Unprocessable Entity` for invalid lengths or missing parameters.
  - `POST /api/v1/customers` creates a customer, returning `201 Created` on success and `409 Conflict` if the email address is already registered.
  - `GET /api/v1/customers` returns all registered customers with `200 OK`.
  - Dependency injection in `app/dependencies.py` properly provides repository and service instances.
  - Application entry point in `app/main.py` mounts routers and initializes cleanly.
- **Verification:** Execute HTTP requests using `httpx.TestClient` and assert returned HTTP status codes (`200`, `201`, `409`, `422`) match specifications.

## T-05 Tests
- **Goal:** Implement comprehensive automated unit and integration tests covering all requirements, acceptance criteria (AC-01 through AC-07), and test scenarios (TS-01 through TS-10).
- **Files:**
  - `tests/__init__.py`
  - `tests/conftest.py`
  - `tests/test_json_customer_repository.py`
  - `tests/test_customer_search_api.py`
- **Acceptance:**
  - `conftest.py` provides a fixture configuring an isolated temporary JSON file path via `tmp_path` for each test.
  - Repository unit tests verify file initialization, search filtering, email lookup, and persistence.
  - API integration tests verify exact matching, partial matching, case-insensitivity, whitespace trimming, query length constraints (0, 1, 2, 100, 101 chars), empty results, creation, and listing.
  - All test cases execute cleanly with 100% pass rate.
- **Verification:** Run `pytest -v` and confirm all test suites pass without warnings or failures.

## T-06 Documentation
- **Goal:** Complete project documentation in `README.md` explaining installation, running the server, executing test suites, and providing API endpoint examples.
- **Files:**
  - `README.md`
- **Acceptance:**
  - `README.md` includes clear setup instructions (`pip install -r requirements.txt`).
  - Includes commands to start the FastAPI server via Uvicorn.
  - Includes commands to execute the `pytest` test suite.
  - Provides example `curl` requests and JSON responses for all endpoints (`/search`, `POST /customers`, `GET /customers`).
- **Verification:** Follow the documented steps in `README.md` sequentially to verify commands and examples function correctly.