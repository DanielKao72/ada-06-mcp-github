from fastapi.testclient import TestClient


def test_search_missing_query_parameter(client: TestClient) -> None:
    response = client.get("/api/v1/customers/search")
    assert response.status_code == 422


def test_search_query_too_short(client: TestClient) -> None:
    response = client.get("/api/v1/customers/search?q=a")
    assert response.status_code == 422


def test_search_query_whitespace_only(client: TestClient) -> None:
    response = client.get("/api/v1/customers/search?q=%20%20%20")
    assert response.status_code == 422


def test_search_query_too_long(client: TestClient) -> None:
    long_query = "a" * 101
    response = client.get(f"/api/v1/customers/search?q={long_query}")
    assert response.status_code == 422


def test_customer_creation_duplicate_email_conflict(client: TestClient) -> None:
    payload = {"name": "Peter Parker", "email": "spidey@dailybugle.com"}
    res1 = client.post("/api/v1/customers", json=payload)
    assert res1.status_code == 201
    data = res1.json()
    assert data["name"] == "Peter Parker"
    assert data["email"] == "spidey@dailybugle.com"

    # Attempt duplicate registration
    res2 = client.post("/api/v1/customers", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_health_check_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
