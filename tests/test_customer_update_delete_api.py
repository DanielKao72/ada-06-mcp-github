import json

import pytest
from fastapi.testclient import TestClient

from app.repositories.json_customer_repository import JsonCustomerRepository
from app.schemas.customer import Customer


def _seed(repo: JsonCustomerRepository, customer_id: str, name: str, email: str) -> Customer:
    customer = Customer(id=customer_id, name=name, email=email, created_at="2026-09-23T23:40:00Z")
    return repo.save(customer)


def _stored(repo: JsonCustomerRepository) -> list:
    return json.loads(repo.file_path.read_text(encoding="utf-8"))


def test_ac08_update_customer_name(client: TestClient, test_repo: JsonCustomerRepository) -> None:
    _seed(test_repo, "cust-123", "John Doe", "john@example.com")

    response = client.patch("/api/v1/customers/cust-123", json={"name": "Johnathan Doe"})

    assert response.status_code == 200
    assert response.json() == {
        "id": "cust-123",
        "name": "Johnathan Doe",
        "email": "john@example.com",
        "created_at": "2026-09-23T23:40:00Z",
    }
    assert _stored(test_repo) == [response.json()]


def test_ac08_update_customer_name_and_email(client: TestClient, test_repo: JsonCustomerRepository) -> None:
    _seed(test_repo, "cust-123", "John Doe", "john@example.com")

    response = client.patch(
        "/api/v1/customers/cust-123",
        json={"name": "Johnathan Doe", "email": "johnathan@example.com"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Johnathan Doe"
    assert data["email"] == "johnathan@example.com"
    assert data["id"] == "cust-123"
    assert data["created_at"] == "2026-09-23T23:40:00Z"
    assert client.get("/api/v1/customers/search?q=johnathan@").json() == [data]


def test_ac09_update_email_collision_conflict(client: TestClient, test_repo: JsonCustomerRepository) -> None:
    _seed(test_repo, "cust-a", "Customer A", "a@domain.com")
    _seed(test_repo, "cust-b", "Customer B", "b@domain.com")

    response = client.patch("/api/v1/customers/cust-b", json={"email": "a@domain.com"})

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]
    assert test_repo.get_by_id("cust-b").email == "b@domain.com"


def test_update_with_own_email_is_not_conflict(client: TestClient, test_repo: JsonCustomerRepository) -> None:
    _seed(test_repo, "cust-b", "Customer B", "b@domain.com")

    response = client.patch("/api/v1/customers/cust-b", json={"email": "b@domain.com"})

    assert response.status_code == 200
    assert response.json()["email"] == "b@domain.com"


def test_ac10_update_non_existent_customer(client: TestClient, test_repo: JsonCustomerRepository) -> None:
    assert client.patch("/api/v1/customers/non-existent-id", json={"name": "Nobody"}).status_code == 404

    _seed(test_repo, "cust-123", "John Doe", "john@example.com")
    response = client.patch("/api/v1/customers/non-existent-id", json={"name": "Nobody"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": ""},
        {"name": "   "},
        {"name": "a" * 151},
        {"email": "not-an-email"},
        {"name": None},
        {"id": "hijacked-id"},
        {"created_at": "2020-01-01T00:00:00Z"},
    ],
)
def test_update_invalid_payload_returns_422(
    client: TestClient, test_repo: JsonCustomerRepository, payload: dict
) -> None:
    _seed(test_repo, "cust-123", "John Doe", "john@example.com")

    response = client.patch("/api/v1/customers/cust-123", json=payload)

    assert response.status_code == 422
    assert test_repo.get_by_id("cust-123").name == "John Doe"


def test_ac11_delete_customer(client: TestClient, test_repo: JsonCustomerRepository) -> None:
    _seed(test_repo, "cust-123", "John Doe", "john@example.com")
    _seed(test_repo, "cust-456", "Jane Roe", "jane@example.com")

    response = client.delete("/api/v1/customers/cust-123")

    assert response.status_code == 204
    assert response.content == b""
    assert [c["id"] for c in _stored(test_repo)] == ["cust-456"]
    assert [c["id"] for c in client.get("/api/v1/customers").json()] == ["cust-456"]


def test_ac12_delete_non_existent_customer(client: TestClient, test_repo: JsonCustomerRepository) -> None:
    _seed(test_repo, "cust-123", "John Doe", "john@example.com")

    response = client.delete("/api/v1/customers/non-existent-id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
    assert len(_stored(test_repo)) == 1


def test_delete_twice_returns_404(client: TestClient, test_repo: JsonCustomerRepository) -> None:
    _seed(test_repo, "cust-123", "John Doe", "john@example.com")

    assert client.delete("/api/v1/customers/cust-123").status_code == 204
    assert client.delete("/api/v1/customers/cust-123").status_code == 404
