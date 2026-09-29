from fastapi.testclient import TestClient


def test_ts01_search_partial_name(client: TestClient) -> None:
    """TS-01 & AC-01: Verify partial name matching with prefix, infix, and suffix substrings."""
    client.post("/api/v1/customers", json={"name": "Alexander Hamilton", "email": "hamilton@treasury.gov"})
    client.post("/api/v1/customers", json={"name": "Bob Smith", "email": "bob@smith.org"})

    # Prefix match
    res_prefix = client.get("/api/v1/customers/search?q=Alex")
    assert res_prefix.status_code == 200
    names = [c["name"] for c in res_prefix.json()]
    assert names == ["Alexander Hamilton"]

    # Infix match
    res_infix = client.get("/api/v1/customers/search?q=xand")
    assert res_infix.status_code == 200
    assert len(res_infix.json()) == 1
    assert res_infix.json()[0]["name"] == "Alexander Hamilton"

    # Suffix match
    res_suffix = client.get("/api/v1/customers/search?q=nder")
    assert res_suffix.status_code == 200
    assert len(res_suffix.json()) == 1
    assert res_suffix.json()[0]["name"] == "Alexander Hamilton"


def test_ts02_search_partial_email(client: TestClient) -> None:
    """TS-02 & AC-02: Verify partial email matching across username, domain, and TLD."""
    client.post("/api/v1/customers", json={"name": "Sarah Connor", "email": "support@acme-corp.com"})

    # Domain match
    res_domain = client.get("/api/v1/customers/search?q=acme")
    assert res_domain.status_code == 200
    assert len(res_domain.json()) == 1
    assert res_domain.json()[0]["email"] == "support@acme-corp.com"

    # Username match
    res_user = client.get("/api/v1/customers/search?q=supp")
    assert res_user.status_code == 200
    assert len(res_user.json()) == 1
    assert res_user.json()[0]["email"] == "support@acme-corp.com"

    # TLD match
    res_tld = client.get("/api/v1/customers/search?q=corp.com")
    assert res_tld.status_code == 200
    assert len(res_tld.json()) == 1


def test_ts03_search_case_insensitivity(client: TestClient) -> None:
    """TS-03: Verify queries in lowercase, uppercase, and mixed casing return identical result sets."""
    client.post("/api/v1/customers", json={"name": "Carlos Gomez", "email": "carlos@domain.com"})

    res_lower = client.get("/api/v1/customers/search?q=carlos")
    res_upper = client.get("/api/v1/customers/search?q=CARLOS")
    res_mixed = client.get("/api/v1/customers/search?q=CaRlOs")

    assert res_lower.status_code == 200
    assert res_upper.status_code == 200
    assert res_mixed.status_code == 200
    assert res_lower.json() == res_upper.json() == res_mixed.json()
    assert len(res_lower.json()) == 1


def test_ts04_search_whitespace_trimming(client: TestClient) -> None:
    """TS-04 & AC-03: Verify leading, trailing, and padded whitespace is trimmed before search."""
    client.post("/api/v1/customers", json={"name": "Carlos Gomez", "email": "carlos@domain.com"})

    res = client.get("/api/v1/customers/search?q=%20%20CARLOS%20%20")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["name"] == "Carlos Gomez"


def test_ts05_search_query_boundary_validation(client: TestClient) -> None:
    """TS-05 & AC-04: Test query parameter length boundary constraints."""
    # 0 chars (missing) -> 422
    assert client.get("/api/v1/customers/search").status_code == 422

    # 1 char -> 422
    assert client.get("/api/v1/customers/search?q=a").status_code == 422

    # 2 chars -> 200
    assert client.get("/api/v1/customers/search?q=ab").status_code == 200

    # 100 chars -> 200
    query_100 = "a" * 100
    assert client.get(f"/api/v1/customers/search?q={query_100}").status_code == 200

    # 101 chars -> 422
    query_101 = "a" * 101
    assert client.get(f"/api/v1/customers/search?q={query_101}").status_code == 422


def test_ts06_search_no_matching_results(client: TestClient) -> None:
    """TS-06 & AC-05: Non-matching queries return HTTP 200 OK with empty list."""
    client.post("/api/v1/customers", json={"name": "Bruce Wayne", "email": "bruce@wayne.corp"})

    res = client.get("/api/v1/customers/search?q=nonexistentterm")
    assert res.status_code == 200
    assert res.json() == []


def test_ts07_customer_creation_persistence(client: TestClient) -> None:
    """TS-07 & AC-06: Create customer with valid UUID, ISO timestamp, and ensure retrievability."""
    payload = {"name": "Diana Prince", "email": "diana@themyscira.gov"}
    res = client.post("/api/v1/customers", json=payload)
    assert res.status_code == 201
    created_customer = res.json()
    assert created_customer["name"] == "Diana Prince"
    assert created_customer["email"] == "diana@themyscira.gov"
    assert "id" in created_customer and len(created_customer["id"]) > 0
    assert "created_at" in created_customer and "T" in created_customer["created_at"]

    # Retrieve and verify it is found in search
    search_res = client.get("/api/v1/customers/search?q=themyscira")
    assert search_res.status_code == 200
    assert len(search_res.json()) == 1
    assert search_res.json()[0]["id"] == created_customer["id"]


def test_ts08_duplicate_email_conflict(client: TestClient) -> None:
    """TS-08: Verify duplicate email registration returns 409 Conflict."""
    payload = {"name": "Clark Kent", "email": "clark@dailyplanet.com"}
    res1 = client.post("/api/v1/customers", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/customers", json={"name": "Superman", "email": "CLARK@DAILYPLANET.COM"})
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_ts09_list_all_customers(client: TestClient) -> None:
    """TS-09 & AC-07: Verify GET /api/v1/customers returns all stored records."""
    # Empty initial state
    res_empty = client.get("/api/v1/customers")
    assert res_empty.status_code == 200
    assert res_empty.json() == []

    # Populate records
    client.post("/api/v1/customers", json={"name": "Customer One", "email": "one@example.com"})
    client.post("/api/v1/customers", json={"name": "Customer Two", "email": "two@example.com"})

    res_all = client.get("/api/v1/customers")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 2
    names = [c["name"] for c in res_all.json()]
    assert "Customer One" in names and "Customer Two" in names
