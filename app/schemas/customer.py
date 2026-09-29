from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class CustomerBase(BaseModel):
    """Base schema defining core customer attributes."""
    name: str = Field(..., min_length=1, max_length=150, description="Customer full name")
    email: EmailStr = Field(..., description="Customer valid email address")

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Customer name cannot be empty or whitespace only")
        return stripped


class CustomerCreate(CustomerBase):
    """Schema for customer creation request payload."""
    pass


class Customer(CustomerBase):
    """Domain and storage entity for a customer record."""
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique customer identifier")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC creation timestamp",
    )

    model_config = ConfigDict(from_attributes=True)


class CustomerResponse(BaseModel):
    """Schema for customer API response payload."""
    id: str
    name: str
    email: EmailStr
    created_at: str

    model_config = ConfigDict(from_attributes=True)
