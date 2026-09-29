"""Custom domain and application exceptions."""


class CustomerAlreadyExistsError(Exception):
    """Raised when attempting to register a customer with an existing email address."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Customer with email '{email}' already exists.")


class CustomerNotFoundError(Exception):
    """Raised when a customer with the given ID does not exist in storage."""

    def __init__(self, customer_id: str) -> None:
        self.customer_id = customer_id
        super().__init__(f"Customer with id '{customer_id}' not found.")
