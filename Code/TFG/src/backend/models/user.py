"""
User Domain Model

Represents a user in the system with all business logic and validation.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from .uuid import generate_uuid, UUIDType


class UserRole(str, Enum):
    """User roles in the system"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserBase(BaseModel):
    """Base user attributes shared across different schemas"""
    email: EmailStr = Field(...)
    name: Optional[str] = Field(default=None,min_length=2)
    contact_person_email: Optional[EmailStr] = None
    contact_person_phone: Optional[PhoneNumber] = None
    diversity_type: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user with email/password"""
    password: str = Field(..., min_length=8)


class UserCreateOAuth(UserBase):
    """Schema for creating a new user via OAuth (Google, Facebook, etc.)"""
    pass  # No password needed for OAuth users


class UserUpdate(BaseModel):
    """Schema for updating an existing user"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=2)
    password: Optional[str] = Field(None, min_length=8)
    contact_person_email: Optional[EmailStr] = None
    contact_person_phone: Optional[PhoneNumber] = None
    diversity_type: Optional[str] = None
    role: Optional[UserRole] = None
    email_verified: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None


class User(UserBase):
    """Complete user model with all attributes (database representation)"""
    id: UUIDType = Field(default_factory=generate_uuid)
    passwordHash: Optional[str] = None  # None for OAuth users
    role: UserRole = Field(default=UserRole.USER)
    created_at: datetime = Field(default_factory=datetime.now)
    email_verified: bool = Field(default=False)
    settings: Dict[str, Any] = Field(default_factory=dict)


class UserResponse(BaseModel):
    """User schema for API responses (excludes sensitive data)"""
    id: UUIDType
    email: EmailStr
    name: str
    contact_person_email: Optional[EmailStr]
    contact_person_phone: Optional[PhoneNumber]
    diversity_type: Optional[str]
    role: UserRole
    created_at: datetime
    email_verified: bool
    settings: Dict[str, Any]
