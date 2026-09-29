from pathlib import Path
import pytest

from app.repositories.json_customer_repository import JsonCustomerRepository
from app.schemas.customer import Customer


def test_repository_creates_missing_file(tmp_path: Path) -> None:
    db_file = tmp_path / "subdir" / "customers.json"
    repo = JsonCustomerRepository(db_file)
    assert db_file.exists()
    assert repo.get_all() == []


def test_repository_save_and_retrieve(tmp_path: Path) -> None:
    db_file = tmp_path / "customers.json"
    repo = JsonCustomerRepository(db_file)
    customer = Customer(name="Alice Johnson", email="alice@example.com")
    repo.save(customer)

    all_records = repo.get_all()
    assert len(all_records) == 1
    assert all_records[0].id == customer.id
    assert all_records[0].name == "Alice Johnson"
    assert all_records[0].email == "alice@example.com"


def test_repository_get_by_id_and_email(tmp_path: Path) -> None:
    db_file = tmp_path / "customers.json"
    repo = JsonCustomerRepository(db_file)
    customer1 = Customer(name="Alice Johnson", email="alice@example.com")
    customer2 = Customer(name="Bob Smith", email="bob@smith.org")
    repo.save(customer1)
    repo.save(customer2)

    assert repo.get_by_id(customer1.id) == customer1
    assert repo.get_by_id(customer2.id) == customer2
    assert repo.get_by_id("nonexistent-id") is None

    assert repo.get_by_email("ALICE@EXAMPLE.COM") == customer1
    assert repo.get_by_email("bob@smith.org") == customer2
    assert repo.get_by_email("unknown@nowhere.com") is None


def test_repository_search_partial_and_case_insensitive(tmp_path: Path) -> None:
    db_file = tmp_path / "customers.json"
    repo = JsonCustomerRepository(db_file)
    c1 = Customer(name="Alexander Hamilton", email="hamilton@treasury.gov")
    c2 = Customer(name="Sarah Connor", email="sarah@cyberdyne.io")
    c3 = Customer(name="George Washington", email="george@mountvernon.org")
    repo.save(c1)
    repo.save(c2)
    repo.save(c3)

    # Search by partial name prefix, infix, suffix
    assert repo.search("alex") == [c1]
    assert repo.search("xand") == [c1]
    assert repo.search("ton") == [c1, c3]  # "Hamilton" and "Washington"

    # Search by partial email
    assert repo.search("cyberdyne") == [c2]
    assert repo.search("mountvernon.org") == [c3]

    # Search case-insensitivity
    assert repo.search("SARAH") == [c2]
    assert repo.search("cYbErDyNe") == [c2]

    # Non-matching search
    assert repo.search("nonexistent") == []


def test_repository_update_existing_and_missing(tmp_path: Path) -> None:
    db_file = tmp_path / "customers.json"
    repo = JsonCustomerRepository(db_file)
    customer = Customer(name="John Doe", email="john@example.com")
    other = Customer(name="Jane Roe", email="jane@example.com")
    repo.save(customer)
    repo.save(other)

    updated = customer.model_copy(update={"name": "Johnathan Doe"})
    assert repo.update(updated) == updated

    # Persisted to disk, order preserved, other records untouched
    reloaded = JsonCustomerRepository(db_file).get_all()
    assert reloaded == [updated, other]

    missing = Customer(name="Ghost", email="ghost@example.com")
    assert repo.update(missing) is None
    assert repo.get_all() == [updated, other]


def test_repository_delete_existing_and_missing(tmp_path: Path) -> None:
    db_file = tmp_path / "customers.json"
    repo = JsonCustomerRepository(db_file)
    customer = Customer(name="John Doe", email="john@example.com")
    other = Customer(name="Jane Roe", email="jane@example.com")
    repo.save(customer)
    repo.save(other)

    assert repo.delete(customer.id) is True
    assert JsonCustomerRepository(db_file).get_all() == [other]

    assert repo.delete(customer.id) is False
    assert repo.delete("nonexistent-id") is False
    assert repo.get_all() == [other]
