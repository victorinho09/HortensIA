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

#The telephone number is stored as a number, so the application must convert its type. Database only stores:
#CC: 34
#Tel: 639104485


FIELD_DESCRIPTIONS = {
    "id": "Unique user identifier (UUID)",
    "email": "User's primary email address",
    "name": "User's full name",
    "password": "User's password (minimum 8 characters)",
    "contact_person_email": "Emergency contact person's email address",
    "contact_person_phone": "Emergency contact person's phone number",
    "contact_person_country_code": "Emergency contact person's phone country code",
    "contact_person_phone_number": "Emergency contact person's phone national number",
    "diversity_type": "Type of diversity or special needs",
    "passwordHash": "Hashed password (None for OAuth users)",
    "role": "User's role in the system",
    "created_at": "Account creation timestamp", #Not inserted by the application. Returned by the database in the future
    "email_verified": "Whether the user's email has been verified",
    "settings": "User preferences and configuration settings (JSON object)"
}



class UserRole(str, Enum):
    """User roles in the system"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserBase(BaseModel):
    """Base user attributes shared across different schemas"""
    email: EmailStr = Field(..., description=FIELD_DESCRIPTIONS["email"])
    name: Optional[str] = Field(default=None, min_length=2, description=FIELD_DESCRIPTIONS["name"])
    contact_person_email: Optional[EmailStr] = Field(default=None, description=FIELD_DESCRIPTIONS["contact_person_email"])
    contact_person_phone: Optional[PhoneNumber] = Field(default=None, description=FIELD_DESCRIPTIONS["contact_person_phone"])
    diversity_type: Optional[str] = Field(default=None, description=FIELD_DESCRIPTIONS["diversity_type"])


class UserCreate(UserBase):
    """Schema for creating a new user with email/password"""
    password: str = Field(..., min_length=8, description=FIELD_DESCRIPTIONS["password"])


class UserCreateOAuth(UserBase):
    """Schema for creating a new user via OAuth (Google, Facebook, etc.)"""
    pass  # No password needed for OAuth users


class UserUpdate(BaseModel):
    """Schema for updating an existing user"""
    email: Optional[EmailStr] = Field(default=None, description=FIELD_DESCRIPTIONS["email"])
    name: Optional[str] = Field(default=None, min_length=2, description=FIELD_DESCRIPTIONS["name"])
    password: Optional[str] = Field(default=None, min_length=8, description=FIELD_DESCRIPTIONS["password"])
    contact_person_email: Optional[EmailStr] = Field(default=None, description=FIELD_DESCRIPTIONS["contact_person_email"])
    contact_person_phone: Optional[PhoneNumber] = Field(default=None, description=FIELD_DESCRIPTIONS["contact_person_phone"])
    diversity_type: Optional[str] = Field(default=None, description=FIELD_DESCRIPTIONS["diversity_type"])
    role: Optional[UserRole] = Field(default=None, description=FIELD_DESCRIPTIONS["role"])
    email_verified: Optional[bool] = Field(default=None, description=FIELD_DESCRIPTIONS["email_verified"])
    settings: Optional[Dict[str, Any]] = Field(default=None, description=FIELD_DESCRIPTIONS["settings"])


class UserInsert(BaseModel):
    """
    Database insertion model with split phone and excluded auto-generated fields.
    Used by repository layer for SQLAlchemy INSERT operations.
    Does not extend from UserBase because has different phone number fields
    """
    id: UUIDType = Field(..., description=FIELD_DESCRIPTIONS["id"])
    email: EmailStr = Field(..., description=FIELD_DESCRIPTIONS["email"])
    name: Optional[str] = Field(default=None, description=FIELD_DESCRIPTIONS["name"])
    contact_person_email: Optional[EmailStr] = Field(default=None, description=FIELD_DESCRIPTIONS["contact_person_email"])
    contact_person_country_code: Optional[int] = Field(default=None, description=FIELD_DESCRIPTIONS["contact_person_country_code"])
    contact_person_phone_number: Optional[int] = Field(default=None, description=FIELD_DESCRIPTIONS["contact_person_phone_number"])
    diversity_type: Optional[str] = Field(default=None, description=FIELD_DESCRIPTIONS["diversity_type"])
    passwordHash: Optional[str] = Field(default=None, description=FIELD_DESCRIPTIONS["passwordHash"])
    role: UserRole = Field(default=UserRole.USER, description=FIELD_DESCRIPTIONS["role"])
    email_verified: bool = Field(default=False, description=FIELD_DESCRIPTIONS["email_verified"])
    settings: Dict[str, Any] = Field(default_factory=dict, description=FIELD_DESCRIPTIONS["settings"])
    # NOTE: created_at is excluded - database will auto-generate with CURRENT_TIMESTAMP


class User(UserBase):
    """Complete user model returned from database (includes auto-generated fields)"""
    id: UUIDType = Field(..., description=FIELD_DESCRIPTIONS["id"])
    passwordHash: Optional[str] = Field(default=None, description=FIELD_DESCRIPTIONS["passwordHash"])
    role: UserRole = Field(default=UserRole.USER, description=FIELD_DESCRIPTIONS["role"])
    created_at: datetime = Field(..., description=FIELD_DESCRIPTIONS["created_at"])
    email_verified: bool = Field(default=False, description=FIELD_DESCRIPTIONS["email_verified"])
    settings: Dict[str, Any] = Field(default_factory=dict, description=FIELD_DESCRIPTIONS["settings"])


class UserResponse(BaseModel):
    """User schema for API responses (excludes sensitive data)"""
    id: UUIDType = Field(..., description=FIELD_DESCRIPTIONS["id"])
    email: EmailStr = Field(..., description=FIELD_DESCRIPTIONS["email"])
    name: str = Field(..., description=FIELD_DESCRIPTIONS["name"])
    contact_person_email: Optional[EmailStr] = Field(default=None, description=FIELD_DESCRIPTIONS["contact_person_email"])
    contact_person_phone: Optional[PhoneNumber] = Field(default=None, description=FIELD_DESCRIPTIONS["contact_person_phone"])
    diversity_type: Optional[str] = Field(default=None, description=FIELD_DESCRIPTIONS["diversity_type"])
    role: UserRole = Field(..., description=FIELD_DESCRIPTIONS["role"])
    created_at: datetime = Field(..., description=FIELD_DESCRIPTIONS["created_at"])
    email_verified: bool = Field(..., description=FIELD_DESCRIPTIONS["email_verified"])
    settings: Dict[str, Any] = Field(..., description=FIELD_DESCRIPTIONS["settings"])
