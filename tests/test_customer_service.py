from pathlib import Path
import pytest

from app.core.exceptions import CustomerAlreadyExistsError
from app.repositories.json_customer_repository import JsonCustomerRepository
from app.schemas.customer import CustomerCreate
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
