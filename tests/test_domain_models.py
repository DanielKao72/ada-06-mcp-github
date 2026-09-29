import pytest
from pydantic import ValidationError

from app.schemas.customer import Customer, CustomerCreate, CustomerResponse, CustomerUpdate


def test_customer_create_valid() -> None:
    data = {"name": "  Alice Johnson  ", "email": "alice@example.com"}
    customer_create = CustomerCreate(**data)
    assert customer_create.name == "Alice Johnson"
    assert customer_create.email == "alice@example.com"


def test_customer_create_invalid_email() -> None:
    with pytest.raises(ValidationError):
        CustomerCreate(name="Bob Smith", email="invalid-email-format")


def test_customer_create_empty_name() -> None:
    with pytest.raises(ValidationError):
        CustomerCreate(name="   ", email="bob@example.com")


def test_customer_entity_defaults() -> None:
    customer = Customer(name="Carlos Gomez", email="carlos@example.com")
    assert customer.id is not None
    assert len(customer.id) > 0
    assert customer.created_at is not None
    assert "T" in customer.created_at


def test_customer_response_serialization() -> None:
    customer = Customer(name="Diana Prince", email="diana@example.com")
    response = CustomerResponse.model_validate(customer)
    assert response.id == customer.id
    assert response.name == "Diana Prince"
    assert response.email == "diana@example.com"
    assert response.created_at == customer.created_at


def test_customer_update_partial_fields() -> None:
    update = CustomerUpdate(name="  Johnathan Doe  ")
    assert update.name == "Johnathan Doe"
    assert update.model_dump(exclude_unset=True) == {"name": "Johnathan Doe"}

    update = CustomerUpdate(email="john@example.com")
    assert update.model_dump(exclude_unset=True) == {"email": "john@example.com"}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"name": ""},
        {"name": "   "},
        {"name": "a" * 151},
        {"email": "invalid-email-format"},
        {"name": None},
        {"email": None},
        {"id": "new-id"},
        {"name": "Valid Name", "created_at": "2020-01-01T00:00:00Z"},
    ],
)
def test_customer_update_invalid_payloads(payload: dict) -> None:
    with pytest.raises(ValidationError):
        CustomerUpdate(**payload)
