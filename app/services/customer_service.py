from typing import List

from app.core.exceptions import CustomerAlreadyExistsError, CustomerNotFoundError
from app.repositories.json_customer_repository import JsonCustomerRepository
from app.schemas.customer import Customer, CustomerCreate, CustomerResponse, CustomerUpdate


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

    def update_customer(self, customer_id: str, customer_in: CustomerUpdate) -> CustomerResponse:
        """Partially updates name and/or email, keeping `id` and `created_at` immutable."""
        existing = self.repository.get_by_id(customer_id)
        if existing is None:
            raise CustomerNotFoundError(customer_id)

        changes = customer_in.model_dump(exclude_unset=True)
        if "email" in changes:
            owner = self.repository.get_by_email(changes["email"])
            if owner is not None and owner.id != customer_id:
                raise CustomerAlreadyExistsError(changes["email"])

        updated = existing.model_copy(update=changes)
        persisted = self.repository.update(updated)
        if persisted is None:
            raise CustomerNotFoundError(customer_id)
        return CustomerResponse.model_validate(persisted)

    def delete_customer(self, customer_id: str) -> None:
        """Permanently removes a customer record."""
        if not self.repository.delete(customer_id):
            raise CustomerNotFoundError(customer_id)
