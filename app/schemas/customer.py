from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


def _strip_non_empty_name(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("Customer name cannot be empty or whitespace only")
    return stripped


class CustomerBase(BaseModel):
    """Base schema defining core customer attributes."""
    name: str = Field(..., min_length=1, max_length=150, description="Customer full name")
    email: EmailStr = Field(..., description="Customer valid email address")

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, value: str) -> str:
        return _strip_non_empty_name(value)


class CustomerCreate(CustomerBase):
    """Schema for customer creation request payload."""
    pass


class CustomerUpdate(BaseModel):
    """Schema for partial customer update payload. `id` and `created_at` are immutable."""
    name: Optional[str] = Field(None, min_length=1, max_length=150, description="Customer full name")
    email: Optional[EmailStr] = Field(None, description="Customer valid email address")

    model_config = ConfigDict(extra="forbid")

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _strip_non_empty_name(value)

    @model_validator(mode="after")
    def validate_fields_provided(self) -> "CustomerUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one of 'name' or 'email' must be provided")
        for field_name in self.model_fields_set:
            if getattr(self, field_name) is None:
                raise ValueError(f"Field '{field_name}' cannot be null")
        return self


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
