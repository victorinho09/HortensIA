"""
SQLAlchemy ORM Models

Database table definitions using SQLAlchemy ORM.
"""

from sqlalchemy import BOOLEAN, Column, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import CITEXT, JSONB, TEXT, UUID
from sqlalchemy.ext.declarative import declarative_base
from backend.utils.uuid import generate_uuid

Base = declarative_base()


class UserTable(Base):
    """
    SQLAlchemy ORM model for users table.
    Maps to database schema with split phone number fields.
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default = generate_uuid())
    
    email = Column(CITEXT, unique=True, nullable=False)
    name = Column(TEXT, nullable=True)
    contact_person_email = Column(CITEXT, nullable=True)
    contact_person_country_code = Column(TEXT, nullable=True)
    contact_person_phone_number = Column(TEXT, nullable=True)
    diversity_type = Column(TEXT, nullable=True)    
    password_hash = Column(TEXT, nullable=False)
    role = Column(TEXT, nullable=False, default="user")
    email_verified = Column(BOOLEAN, nullable=False, default=False)
    settings = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

class SessionTable(Base):
    """
    SQLAlchemy ORM model for sessions table.
    Stores active user sessions for authentication
    """
    __tablename__ = "sessions"

    #Primary key
    session_id = Column(UUID(as_uuid=True), primary_key=True,default = generate_uuid())

    #Foreign Key
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)

    created_at= Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True),nullable=False)
    last_activity = Column(DateTime(timezone=True),nullable=False)
