import json
from pathlib import Path
from typing import List, Optional

from app.schemas.customer import Customer


class JsonCustomerRepository:
    """Repository handling persistence and queries for customers in a local JSON file."""

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)
        self._ensure_storage_initialized()

    def _ensure_storage_initialized(self) -> None:
        """Ensures the parent directory and JSON storage file exist."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write_raw_data([])

    def _read_raw_data(self) -> List[dict]:
        """Reads and parses raw dictionary records from the JSON file."""
        self._ensure_storage_initialized()
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_raw_data(self, data: List[dict]) -> None:
        """Writes the raw list of dictionaries to the JSON file with clean formatting."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all(self) -> List[Customer]:
        """Retrieves all customers stored in the JSON file."""
        raw_items = self._read_raw_data()
        return [Customer.model_validate(item) for item in raw_items]

    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """Finds a customer by their unique ID."""
        for customer in self.get_all():
            if customer.id == customer_id:
                return customer
        return None

    def get_by_email(self, email: str) -> Optional[Customer]:
        """Finds a customer by their exact email address (case-insensitive)."""
        normalized_email = email.strip().lower()
        for customer in self.get_all():
            if customer.email.lower() == normalized_email:
                return customer
        return None

    def search(self, term: str) -> List[Customer]:
        """Searches customers by case-insensitive partial substring match in name or email."""
        normalized_term = term.strip().lower()
        if not normalized_term:
            return []

        all_customers = self.get_all()
        return [
            customer
            for customer in all_customers
            if normalized_term in customer.name.lower()
            or normalized_term in customer.email.lower()
        ]

    def save(self, customer: Customer) -> Customer:
        """Appends and persists a customer to the JSON file."""
        customers = self.get_all()
        customers.append(customer)
        raw_data = [c.model_dump(mode="json") for c in customers]
        self._write_raw_data(raw_data)
        return customer
