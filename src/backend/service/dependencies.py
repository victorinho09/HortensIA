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
