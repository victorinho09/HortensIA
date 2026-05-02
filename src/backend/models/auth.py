"""
Authentication Models

Models for login requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field

from backend.models.user import UserResponse

class LoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (minimum 8 characters)")

class LoginResponse(BaseModel):
    """Response model for successful login"""
    session_id: str = Field(..., description="Session identifier for authentication")
    user: UserResponse = Field(..., description="User information without sensitive data")