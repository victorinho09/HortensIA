"""
Backend Domain Models

This package contains the core domain models and business logic
that are independent of the API layer and database implementation.
"""

from .user import (
    User, 
    UserBase,
    UserCreate, 
    UserCreateOAuth,
    UserUpdate,
    UserInsert,
    UserResponse,
    UserRole
)
from .uuid import UUIDType, generate_uuid, validate_uuid, uuid_to_str
from .hash import hash_password, verify_password, needs_rehash

__all__ = [
    # User models
    "User",
    "UserBase",
    "UserCreate",
    "UserCreateOAuth",
    "UserUpdate",
    "UserInsert",
    "UserResponse",
    "UserRole",
    # UUID utilities
    "UUIDType",
    "generate_uuid",
    "validate_uuid",
    "uuid_to_str",
    # Password hashing
    "hash_password",
    "verify_password",
    "needs_rehash",
]
