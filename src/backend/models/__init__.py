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
    PasswordChange,
    UserInsert,
    UserResponse,
    UserRole
)
from backend.utils.uuid import UUIDType, generate_uuid, validate_uuid, uuid_to_str, str_to_uuid
from backend.utils.hash import hash_password, verify_password, needs_rehash
from .auth import AuthIdentityInsert, AuthIdentity, Provider
from .websocket import (
    ClientMessageType,
    FrameMessage,
    ServerMessageTypes,
    AlertMessage,
    AlertSeverity,
    DetectedObject,
    DetectionMessage,
    StatusMessage,
    ErrorMessage,
)

from backend.ai.yolo.coco_taxonomy import COCOSupercategory

__all__ = [
    # User models
    "User",
    "UserBase",
    "UserCreate",
    "UserCreateOAuth",
    "UserUpdate",
    "PasswordChange",
    "UserInsert",
    "UserResponse",
    "UserRole",
    # UUID utilities
    "UUIDType",
    "generate_uuid",
    "validate_uuid",
    "uuid_to_str",
    "str_to_uuid",
    # Password hashing
    "hash_password",
    "verify_password",
    "needs_rehash",
    # Auth identity models
    "AuthIdentityInsert",
    "AuthIdentity",
    "Provider",
    # Websocket message models
    "ClientMessageType",
    "FrameMessage",
    "ServerMessageTypes",
    "AlertSeverity",
    "DetectedObject",
    "AlertMessage",
    "DetectionMessage",
    "StatusMessage",
    "ErrorMessage",
    # AI supercategory model
    "COCOSupercategory"
]
