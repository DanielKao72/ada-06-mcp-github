from fastapi import Depends

from app.core.config import settings
from app.repositories.json_customer_repository import JsonCustomerRepository
from app.services.customer_service import CustomerService


def get_customer_repository() -> JsonCustomerRepository:
    """Provides an instance of JsonCustomerRepository configured with the application storage path."""
    return JsonCustomerRepository(settings.customers_file_path)


def get_customer_service(
    repository: JsonCustomerRepository = Depends(get_customer_repository),
) -> CustomerService:
    """Provides an instance of CustomerService injected with the customer repository."""
    return CustomerService(repository)
