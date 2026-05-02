"""
Session repository - Database access layer for Session operations

"""

from datetime import datetime, timedelta
from backend.models.user import UserResponse, User
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from backend.databases.models import SessionTable, UserTable
from backend.utils.uuid import UUIDType, generate_uuid,str_to_uuid
from typing import Optional

EXPIRES_DAYS = 30

class SessionRepository:
    def __init__(self,db_session: Session):
        """
        Initialize repository with database session
        """

        self.db = db_session

    async def create_session(self,user_id: str | UUIDType, expires_days: int=EXPIRES_DAYS ) -> str:
        """
        Creates a new session for a user
        """

        if isinstance(user_id,str):
            user_id = str_to_uuid(user_id)

        session_id = generate_uuid()
        expires_at = datetime.now() + timedelta(days=expires_days)
        current_time = datetime.now()

        new_session = SessionTable(
            session_id = session_id,
            user_id = user_id,
            expires_at = expires_at,
            last_activity = current_time
        )

        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        
        return str(session_id)

    async def get_user_by_session(self,session_id: str | UUIDType) -> Optional[UserResponse]:
        query = (
            select(UserTable)
            .join(SessionTable, SessionTable.user_id == UserTable.id)
            .where(SessionTable.session_id == session_id)
            .where(SessionTable.expires_at  > datetime.now())
        )
        result = self.db.execute(query)
        user_table = result.scalar_one_or_none()
        if user_table:

            user = self._row_to_user(user_table)
            return user.user_to_user_response()

        return None

    async def delete_session(self, session_id: str | UUIDType) -> bool:
        query = delete(SessionTable).where(SessionTable.session_id == session_id)
        result = self.db.execute(query)
        self.db.commit()
        return result.rowcount > 0
    
    async def delete_expired_sessions(self) -> int:
        """
        Utility function to clean up expired sessions

        Returns number of sessions deleted
        """
        query = delete(SessionTable).where(SessionTable.expires_at < datetime.now())
        result = self.db.execute(query)
        self.db.commit()
        return result.rowcount
    
    async def update_last_activity(self,session_id: str | UUIDType,extend_by_days: int = EXPIRES_DAYS) -> bool:
        """
        Updates the last activity timestamp for a sessin
        """
        from sqlalchemy import update

        new_expires_at = datetime.now() + timedelta(days=extend_by_days)

        query = (
            update(SessionTable)
            .where(SessionTable.session_id == session_id)
            .values(
                last_activity = datetime.now(),
                expires_at = new_expires_at
            )
        )
        result = self.db.execute(query)
        self.db.commit()
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
            created_at=user_row.created_at
        )


