"""
User Repository - Database access layer for User operations
"""
from typing import Optional
from backend.models.auth import Provider
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from backend.models.user import UserInsert, User
from backend.databases.models import AuthIdentities, UserTable
from backend.utils.uuid import UUIDType, str_to_uuid


class UserRepository:
    """
    Repository pattern for User database operations.
    Separates data access logic from business logic.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize repository with database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    async def exists_user(self, email: str) -> bool:
        """
        Check if a user exists in the database

        Args:
            email: User's email address
        Returns: 
            True if the user exists, False if not
        """
        existing_user = await self.get_by_email(email)
        return existing_user is not None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User object if found, None otherwise
        """
        # Build SELECT query using SQLAlchemy
        query = select(UserTable).where(UserTable.email == email)
        result = self.db.execute(query)
        user_row = result.scalar_one_or_none()
        
        if user_row:
            # Convert SQLAlchemy model to Pydantic model
            return self._row_to_user(user_row)
        return None
    
    async def get_by_email_with_password(self,email: str):
        """
        Get user with password hash for authentication
        """
        
        query = (
            select(UserTable,AuthIdentities.password_hash) #This returns a tuple (UserTable,password_hash)
            .join(AuthIdentities,AuthIdentities.user_id == UserTable.id)
            .where(UserTable.email == email)
            .where(AuthIdentities.provider == Provider.PASSWORD)
        )
        result = self.db.execute(query)
        row = result.first()

        if row:
            user, password_hash = row
            return {
                "user": self._row_to_user(user),  # Convert UserTable to User (Pydantic)
                "password_hash": password_hash
            }
        return None
    
    async def create(self, user: UserInsert) -> User:
        """
        Save a new user to the database.
        
        Args:
            user: UserInsert object with user data
            
        Returns:
            User object with generated ID and timestamps
        """
        # Convert Pydantic model to SQLAlchemy model
        user_data = user.model_dump()
        db_user = UserTable(**user_data)
        
        # Add and commit to database
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)  # Refresh to get generated fields
        
        return self._row_to_user(db_user)
    
    async def get_by_id(self, user_id: str | UUIDType) -> Optional[User]:
        """
        Retrieve a user by their ID.
        
        Args:
            user_id: User's unique identifier (string or UUID)
            
        Returns:
            User object if found, None otherwise
        """
        # Convert string to UUID if needed
        if isinstance(user_id, str):
            user_id = str_to_uuid(user_id)
        
        # Build SELECT query by ID
        query = select(UserTable).where(UserTable.id == user_id)
        result = self.db.execute(query)
        user_row = result.scalar_one_or_none()
        
        if user_row:
            return self._row_to_user(user_row)
        return None
    
    async def update(self, user_id: str | UUIDType, user_data: dict) -> Optional[User]:
        """
        Update an existing user's information.
        
        Args:
            user_id: User's unique identifier
            user_data: Dictionary with fields to update
            
        Returns:
            Updated User object if found, None otherwise
        """
        # Convert string to UUID if needed
        if isinstance(user_id, str):
            user_id = str_to_uuid(user_id)
        
        # Fields that cannot be set to null (only email is truly required)
        REQUIRED_FIELDS = {'email'}
        
        # Filter out null values for required fields only
        # Optional fields (name, contact_person_*, diversity_type) can be set to null
        filtered_data = {}
        for key, value in user_data.items():
            if value is None and key in REQUIRED_FIELDS:
                # Skip null values for required fields
                continue
            filtered_data[key] = value
        
        if not filtered_data:
            # No updates to perform, just return current user
            return await self.get_by_id(user_id)
        
        # Build UPDATE query
        query = (
            update(UserTable)
            .where(UserTable.id == user_id)
            .values(**filtered_data)
        )
        
        result = self.db.execute(query)
        self.db.commit()
        
        # Check if any row was updated
        if result.rowcount == 0:
            return None
        
        # Return updated user
        return await self.get_by_id(user_id)
    
    async def delete(self, user_id: str | UUIDType) -> bool:
        """
        Delete a user from the database.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        # Convert string to UUID if needed
        if isinstance(user_id, str):
            user_id = str_to_uuid(user_id)
        
        # Build DELETE query
        query = delete(UserTable).where(UserTable.id == user_id)
        
        result = self.db.execute(query)
        self.db.commit()
        
        # Return True if a row was deleted
        return result.rowcount > 0
    
    def _row_to_user(self, user_row: UserTable) -> User:
        """
        Convert SQLAlchemy UserTable row to Pydantic User model.
        
        Args:
            user_row: SQLAlchemy UserTable instance
            
        Returns:
            Pydantic User model
        """
        return User(
            id=str(user_row.id),
            email=user_row.email,
            name=user_row.name,
            contact_person_email=user_row.contact_person_email,
            contact_person_country_code=user_row.contact_person_country_code,
            contact_person_phone_number=user_row.contact_person_phone_number,
            diversity_type=user_row.diversity_type,
            passwordHash=None,  # Don't include password hash in User model
            role=user_row.role,
            email_verified=user_row.email_verified,
            settings=user_row.settings,
            created_at=user_row.created_at
        )
