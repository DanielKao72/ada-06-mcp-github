"""Custom domain and application exceptions."""


class CustomerAlreadyExistsError(Exception):
    """Raised when attempting to register a customer with an existing email address."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Customer with email '{email}' already exists.")
