"""
Session repository - Database access layer for Session operations

"""

from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from backend.databases.models import SessionTable, UserTable
from backend.databases.connection import get_session
from backend.models.uuid import UUIDType, generate_uuid,str_to_uuid

class SessionRepository:
    def __init__(self,db_session: Session):
        """
        Initialize repository with database session
        """

        self.db = db_session

    async def create_session(self,user_id: str | UUIDType, expires_days: int=30 ) -> str:
        """
        Creates a new session for a user
        """

        if isinstance(user_id,str):
            user_id = str_to_uuid(user_id)

        session_id = generate_uuid()
        expires_at = datetime.now() + timedelta(days=expires_days)

        new_session = SessionTable(
            session_id = session_id,
            user_id = user_id,
            expires_at = expires_at
        )

        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        
        return str(session_id)

    async def get_user_by_session(self,session_id: str | UUIDType) -> Optional[UserTable]:
        query = (
            select(UserTable)
            .join(SessionTable, SessionTable.user_id == UserTable.id)
            .where(SessionTable.session_id == session_id)
            .where(SessionTable.expires_at  > datetime.now())
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

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
    
    async def update_last_activity(self,session_id: str | UUIDType) -> bool:
        """
        Updates the last activity timestamp for a sessin
        """
        from sqlalchemy import update

        query = (
            update(SessionTable)
            .where(SessionTable.session_id == session_id)
            .values(last_activity = datetime.now())
        )
        result = self.db.execute(query)
        self.db.commit()
        return result.rowcount > 0


