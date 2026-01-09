"""
User Domain Model

Represents a user in the system with all business logic and validation.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from .uuid import generate_uuid, UUIDType


class UserBase(BaseModel):
    """Base user attributes shared across different schemas"""
    email: EmailStr
    full_name: str
    contact_person_email: EmailStr
    contact_person_phone: PhoneNumber
    functional_diversity_type: str


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating an existing user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    contact_person_email: Optional[EmailStr] = None
    contact_person_phone: Optional[PhoneNumber] = None
    functional_diversity_type: Optional[str] = None


class User(UserBase):
    """Complete user model with all attributes"""
    id: UUIDType = Field(default_factory=generate_uuid)
