from pathlib import Path
from typing import Generator
import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_customer_repository
from app.main import app
from app.repositories.json_customer_repository import JsonCustomerRepository


@pytest.fixture
def test_repo(tmp_path: Path) -> JsonCustomerRepository:
    """Fixture providing an isolated JSON repository backed by a temporary file."""
    temp_file = tmp_path / "test_customers.json"
    return JsonCustomerRepository(temp_file)


@pytest.fixture
def client(test_repo: JsonCustomerRepository) -> Generator[TestClient, None, None]:
    """Fixture providing a FastAPI TestClient configured to use the isolated test repository."""
    app.dependency_overrides[get_customer_repository] = lambda: test_repo
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
