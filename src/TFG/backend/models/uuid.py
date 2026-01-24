"""
UUID Model and Utilities

Provides UUID type definitions and utilities for use across all domain models.
"""

from uuid import UUID, uuid4
from typing import Annotated
from pydantic import Field, BeforeValidator


def validate_uuid(value) -> UUID:
    """
    Validate and convert string to UUID.
    
    Args:
        value: String representation of UUID or UUID object
        
    Returns:
        UUID object
        
    Raises:
        ValueError: If value cannot be converted to UUID
    """
    if isinstance(value, UUID):
        return value
    if isinstance(value, str):
        return UUID(value)
    raise ValueError(f"Invalid UUID format: {value}")


# Custom UUID type with validation
UUIDType = Annotated[
    UUID,
    BeforeValidator(validate_uuid),
    Field(description="Unique identifier in UUID format")
]


def generate_uuid() -> UUID:
    """
    Generate a new UUID4.
    
    Returns:
        New UUID4 object
    """
    return uuid4()


def uuid_to_str(uuid_obj: UUID) -> str:
    """
    Convert UUID to string representation.
    
    Args:
        uuid_obj: UUID object
        
    Returns:
        String representation of UUID
    """
    return str(uuid_obj)


