"""
User Domain Model

Represents a user in the system with all business logic and validation.
"""

from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from backend.utils.uuid import generate_uuid, UUIDType


FIELD_DESCRIPTIONS = {
    "id": "Unique user identifier (UUID)",
    "email": "User's primary email address",
    "name": "User's full name",
    "password": "User's password (minimum 8 characters)",
    "contact_person_email": "Emergency contact person's email address",
    "contact_person_country_code": "Emergency contact person's phone country code",
    "contact_person_phone_number": "Emergency contact person's phone national number, not including the country code",
    "diversity_type": "Type of diversity or special needs",
    "passwordHash": "Hashed password",
    "role": "User's role in the system",
    "created_at": "Account creation timestamp", #Not inserted by the application. Returned by the database in the future
    "email_verified": "Whether the user's email has been verified"
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
    #Country code and phone number must be strings, if not, there are problems with the number of 0's
    contact_person_country_code: Optional[str] = Field(default=None, max_length=3,description=FIELD_DESCRIPTIONS["contact_person_country_code"])
    contact_person_phone_number: Optional[str] = Field(default=None, min_length=6, max_length=15,description=FIELD_DESCRIPTIONS["contact_person_phone_number"])
    diversity_type: Optional[str] = Field(default=None, description=FIELD_DESCRIPTIONS["diversity_type"])


class UserCreate(UserBase):
    """Schema for creating a new user with email/password"""
    password: str = Field(..., min_length=8, description=FIELD_DESCRIPTIONS["password"])


class UserUpdate(BaseModel):
    """Schema for updating an existing user"""
    email: Optional[EmailStr] = Field(default=None, description=FIELD_DESCRIPTIONS["email"])
    name: Optional[str] = Field(default=None, min_length=2, description=FIELD_DESCRIPTIONS["name"])
    contact_person_email: Optional[EmailStr] = Field(default=None, description=FIELD_DESCRIPTIONS["contact_person_email"])
    #Country code and phone number must be strings, if not, there are problems with the number of 0's
    contact_person_country_code: Optional[str] = Field(default=None,max_length=4, description=FIELD_DESCRIPTIONS["contact_person_country_code"])
    contact_person_phone_number: Optional[str] = Field(default=None,min_length=6,max_length=15,description=FIELD_DESCRIPTIONS["contact_person_phone_number"])
    diversity_type: Optional[str] = Field(default=None, description=FIELD_DESCRIPTIONS["diversity_type"])
    role: Optional[UserRole] = Field(default=None, description=FIELD_DESCRIPTIONS["role"])
    email_verified: Optional[bool] = Field(default=None, description=FIELD_DESCRIPTIONS["email_verified"])

class PasswordChange(BaseModel):
    """
    Schema for changing user password
    """
    current_password: str = Field(...,min_length=8,description="Current password for verification")
    new_password: str = Field(...,min_length=8,description="New password to change")

class UserInsert(UserBase):
    """
    Database insertion model with split phone and excluded auto-generated fields.
    Used by repository layer for SQLAlchemy INSERT operations.
    Extends from UserBase and adds database-specific fields.
    Includes passwordHash for password-based authentication.
    """
    id: UUIDType = Field(default_factory=generate_uuid, description=FIELD_DESCRIPTIONS["id"])
    passwordHash: str = Field(..., min_length=1, description=FIELD_DESCRIPTIONS["passwordHash"])
    role: UserRole = Field(default=UserRole.USER, description=FIELD_DESCRIPTIONS["role"])
    email_verified: bool = Field(default=False, description=FIELD_DESCRIPTIONS["email_verified"])
    # NOTE: created_at is excluded - database will auto-generate with CURRENT_TIMESTAMP

class UserResponse(UserBase):
    """User schema for API responses (excludes sensitive data)"""
    id: UUIDType = Field(..., description=FIELD_DESCRIPTIONS["id"])
    role: UserRole = Field(..., description=FIELD_DESCRIPTIONS["role"])
    created_at: datetime = Field(..., description=FIELD_DESCRIPTIONS["created_at"])
    email_verified: bool = Field(..., description=FIELD_DESCRIPTIONS["email_verified"])

class User(UserBase):
    """Complete user model returned from database (includes auto-generated fields)"""
    id: UUIDType = Field(..., description=FIELD_DESCRIPTIONS["id"])
    passwordHash: Optional[str] = Field(default=None, description=FIELD_DESCRIPTIONS["passwordHash"])
    role: UserRole = Field(default=UserRole.USER, description=FIELD_DESCRIPTIONS["role"])
    created_at: datetime = Field(..., description=FIELD_DESCRIPTIONS["created_at"])
    email_verified: bool = Field(default=False, description=FIELD_DESCRIPTIONS["email_verified"])

    def user_to_user_response(self) -> UserResponse:
        """
        Convert User to UserResponse (safe for API responses).
        Excludes sensitive fields like passwordHash.
        
        Returns:
            UserResponse object with public user data
        """
        return UserResponse(
            id=self.id,
            email=self.email,
            name=self.name,
            contact_person_email=self.contact_person_email,
            contact_person_country_code=self.contact_person_country_code,
            contact_person_phone_number=self.contact_person_phone_number,
            diversity_type=self.diversity_type,
            role=self.role,
            created_at=self.created_at,
            email_verified=self.email_verified
        )



