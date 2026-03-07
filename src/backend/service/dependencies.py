from fastapi import HTTPException, status, Header, Depends
from sqlalchemy.orm import Session
from backend.models.user import UserResponse
from backend.databases.session_repository import SessionRepository
from backend.databases.connection import get_db
from backend.utils.uuid import validate_uuid

async def get_current_user_from_session(
    authorization: str = Header(..., description= "Session ID or authentication"),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Dependency to validate session and return authenticated user.
    
    Validates:
    - UUID format
    - Session exists and not expired
    - Updates last activity
    
    Returns:
        UserResponse: Authenticated user information
        
    Raises:
        HTTPException 401: Invalid or expired session
    """
    try: 
        validate_uuid(authorization)
    except ValueError:
        raise HTTPException(
            status_code = 401,
            detail= "Invalid or expired session"
        )

    session_repo = SessionRepository(db)
    user_response = await session_repo.get_user_by_session(authorization)

    if not user_response:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid or expired session"
        )

    await session_repo.update_last_activity(authorization)
    return user_response

async def validate_session(session_id: str, db: Session) -> UserResponse | None:
    """
    Validates a session for WebSocket connections.
    Unlike get_current_user_from_session, this does not use FastAPI Depends
    and returns None instead of raising an exception, so the caller can
    decide how to handle the failure

    Returns:
        UserResponse if session is valid, None otherwise.
    """
    try:
        validate_uuid(session_id)
    except ValueError:
        return None
    
    session_repo = SessionRepository(db)
    return await session_repo.get_user_by_session(session_id)
