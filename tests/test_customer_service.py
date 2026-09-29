from pathlib import Path
import pytest

from app.core.exceptions import CustomerAlreadyExistsError, CustomerNotFoundError
from app.repositories.json_customer_repository import JsonCustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.customer_service import CustomerService


def test_service_create_customer_and_prevent_duplicates(tmp_path: Path) -> None:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    service = CustomerService(repo)

    create_data = CustomerCreate(name="Bruce Wayne", email="bruce@wayne.corp")
    response = service.create_customer(create_data)

    assert response.id is not None
    assert response.name == "Bruce Wayne"
    assert response.email == "bruce@wayne.corp"

    # Attempting to create duplicate email should raise CustomerAlreadyExistsError
    with pytest.raises(CustomerAlreadyExistsError):
        service.create_customer(CustomerCreate(name="Another Bruce", email="BRUCE@WAYNE.CORP"))


def test_service_search_customers_with_trimming(tmp_path: Path) -> None:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    service = CustomerService(repo)

    service.create_customer(CustomerCreate(name="Clark Kent", email="clark@dailyplanet.com"))
    service.create_customer(CustomerCreate(name="Diana Prince", email="diana@themyscira.gov"))

    # Search with whitespace padding
    results = service.search_customers("   KENT   ")
    assert len(results) == 1
    assert results[0].name == "Clark Kent"

    # Search email
    results = service.search_customers("themyscira")
    assert len(results) == 1
    assert results[0].name == "Diana Prince"

    # Search non-matching
    assert service.search_customers("gotham") == []


def test_service_get_all_customers(tmp_path: Path) -> None:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    service = CustomerService(repo)

    assert service.get_all_customers() == []

    service.create_customer(CustomerCreate(name="Barry Allen", email="barry@centralcity.gov"))
    assert len(service.get_all_customers()) == 1


def test_service_update_customer_keeps_immutable_fields(tmp_path: Path) -> None:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    service = CustomerService(repo)
    created = service.create_customer(CustomerCreate(name="John Doe", email="john@example.com"))

    updated = service.update_customer(created.id, CustomerUpdate(name="Johnathan Doe"))
    assert updated.id == created.id
    assert updated.created_at == created.created_at
    assert updated.name == "Johnathan Doe"
    assert updated.email == "john@example.com"

    updated = service.update_customer(created.id, CustomerUpdate(email="johnathan@example.com"))
    assert updated.name == "Johnathan Doe"
    assert updated.email == "johnathan@example.com"
    assert repo.get_by_id(created.id).email == "johnathan@example.com"


def test_service_update_customer_email_conflict_and_own_email(tmp_path: Path) -> None:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    service = CustomerService(repo)
    service.create_customer(CustomerCreate(name="Customer A", email="a@domain.com"))
    b = service.create_customer(CustomerCreate(name="Customer B", email="b@domain.com"))

    with pytest.raises(CustomerAlreadyExistsError):
        service.update_customer(b.id, CustomerUpdate(email="A@DOMAIN.COM"))
    assert repo.get_by_id(b.id).email == "b@domain.com"

    # Re-submitting the customer's own email is not a collision
    same = service.update_customer(b.id, CustomerUpdate(email="b@domain.com"))
    assert same.email == "b@domain.com"


def test_service_update_and_delete_missing_customer(tmp_path: Path) -> None:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    service = CustomerService(repo)

    with pytest.raises(CustomerNotFoundError):
        service.update_customer("non-existent-id", CustomerUpdate(name="Nobody"))
    with pytest.raises(CustomerNotFoundError):
        service.delete_customer("non-existent-id")


def test_service_delete_customer(tmp_path: Path) -> None:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    service = CustomerService(repo)
    created = service.create_customer(CustomerCreate(name="John Doe", email="john@example.com"))

    service.delete_customer(created.id)
    assert repo.get_by_id(created.id) is None
    assert service.get_all_customers() == []
