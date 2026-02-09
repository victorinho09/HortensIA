"""
Authentication Identity Repository - Database access layer for auth_identities operations
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.models.auth import AuthIdentityInsert, AuthIdentity
from backend.models.uuid import UUIDType, str_to_uuid
from backend.databases.models import AuthIdentities


class AuthRepository:
    """
    Repository pattern for authentication identity database operations.
    Handles password storage and OAuth identity management.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize repository with database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    async def create(self, auth_identity: AuthIdentityInsert) -> AuthIdentity:
        """
        Save a new authentication identity to the database.
        
        Args:
            auth_identity: AuthIdentityInsert object with auth data
            
        Returns:
            AuthIdentity object with generated timestamps
        """
        # Convert Pydantic model to SQLAlchemy model
        auth_data = auth_identity.model_dump()
        db_auth = AuthIdentities(**auth_data)
        
        # Add and commit to database
        self.db.add(db_auth)
        self.db.commit()
        self.db.refresh(db_auth)  # Refresh to get generated fields
        
        return self._row_to_auth_identity(db_auth)
    
    async def get_by_user_and_provider(self, user_id: str | UUIDType, provider: str) -> Optional[AuthIdentity]:
        """
        Retrieve an authentication identity by user ID and provider.
        
        Args:
            user_id: User's unique identifier
            provider: Authentication provider (e.g., 'local', 'google')
            
        Returns:
            AuthIdentity object if found, None otherwise
        """
        # Convert string to UUID if needed
        if isinstance(user_id, str):
            user_id = str_to_uuid(user_id)
        
        # Build SELECT query
        query = select(AuthIdentities).where(
            AuthIdentities.user_id == user_id,
            AuthIdentities.provider == provider
        )
        result = self.db.execute(query)
        auth_row = result.scalar_one_or_none()
        
        if auth_row:
            return self._row_to_auth_identity(auth_row)
        return None
    
    async def get_by_user_id(self, user_id: str | UUIDType) -> list[AuthIdentity]:
        """
        Retrieve all authentication identities for a user.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            List of AuthIdentity objects
        """
        # Convert string to UUID if needed
        if isinstance(user_id, str):
            user_id = str_to_uuid(user_id)
        
        # Build SELECT query
        query = select(AuthIdentities).where(AuthIdentities.user_id == user_id)
        result = self.db.execute(query)
        auth_rows = result.scalars().all()
        
        return [self._row_to_auth_identity(row) for row in auth_rows]
    
    def _row_to_auth_identity(self, auth_row: AuthIdentities) -> AuthIdentity:
        """
        Convert SQLAlchemy AuthIdentities row to Pydantic AuthIdentity model.
        
        Args:
            auth_row: SQLAlchemy AuthIdentities instance
            
        Returns:
            Pydantic AuthIdentity model
        """
        return AuthIdentity(
            id=str(auth_row.id),
            user_id=str(auth_row.user_id),
            provider=auth_row.provider,
            provider_user_id=auth_row.provider_user_id,
            password_hash=auth_row.password_hash,
            created_at=auth_row.created_at
        )
