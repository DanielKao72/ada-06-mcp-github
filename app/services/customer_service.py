from typing import List

from app.core.exceptions import CustomerAlreadyExistsError
from app.repositories.json_customer_repository import JsonCustomerRepository
from app.schemas.customer import Customer, CustomerCreate, CustomerResponse


class CustomerService:
    """Service handling business logic, validation coordination, and data transformation for customers."""

    def __init__(self, repository: JsonCustomerRepository) -> None:
        self.repository = repository

    def search_customers(self, query: str) -> List[CustomerResponse]:
        """Performs case-insensitive partial substring search across customer names and emails."""
        cleaned_query = query.strip()
        matched_customers = self.repository.search(cleaned_query)
        return [CustomerResponse.model_validate(c) for c in matched_customers]

    def create_customer(self, customer_in: CustomerCreate) -> CustomerResponse:
        """Validates uniqueness, creates and persists a new customer entity."""
        existing = self.repository.get_by_email(customer_in.email)
        if existing is not None:
            raise CustomerAlreadyExistsError(customer_in.email)

        customer = Customer(name=customer_in.name, email=customer_in.email)
        persisted = self.repository.save(customer)
        return CustomerResponse.model_validate(persisted)

    def get_all_customers(self) -> List[CustomerResponse]:
        """Retrieves all registered customers."""
        all_customers = self.repository.get_all()
        return [CustomerResponse.model_validate(c) for c in all_customers]
