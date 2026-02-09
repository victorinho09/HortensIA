"""
Authentication Identity Models

Models for managing user authentication identities (passwords, OAuth providers, etc.)
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .uuid import UUIDType, generate_uuid

class Provider(str, Enum):
    """Providers available"""
    PASSWORD = "password"


class AuthIdentityInsert(BaseModel):
    """
    Model for inserting authentication identity into database.
    Links a user to their authentication method (password, OAuth, etc.)
    """
    id: UUIDType = Field(default_factory=generate_uuid, description="Unique identifier for this auth identity")
    user_id: UUIDType = Field(..., description="User ID this auth identity belongs to")
    provider: str = Field(..., description="Authentication provider (local, google, facebook, etc.)")
    provider_user_id: Optional[str] = Field(default=None, description="User ID from the provider (for OAuth)")
    password_hash: Optional[str] = Field(default=None, description="Hashed password (for local auth)")
    # NOTE: created_at is excluded - database will auto-generate


class AuthIdentity(BaseModel):
    """
    Complete authentication identity model returned from database.
    """
    id: UUIDType = Field(..., description="Unique identifier for this auth identity")
    user_id: UUIDType = Field(..., description="User ID this auth identity belongs to")
    provider: str = Field(..., description="Authentication provider")
    provider_user_id: Optional[str] = Field(default=None, description="User ID from the provider")
    password_hash: Optional[str] = Field(default=None, description="Hashed password")
    created_at: datetime = Field(..., description="When this auth identity was created")
