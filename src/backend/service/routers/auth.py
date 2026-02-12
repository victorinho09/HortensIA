"""
Users Router
"""
from backend.databases.session_repository import SessionRepository
from fastapi import APIRouter, HTTPException, status, Response, Depends, Header
from backend.models.user import UserCreate, UserResponse, UserInsert
from backend.models.auth import AuthIdentityInsert, LoginRequest, LoginResponse
from backend.utils.hash import hash_password, verify_password
from backend.utils.uuid import generate_uuid
from backend.models.auth import Provider
from backend.databases.user_repository import UserRepository
from backend.databases.auth_repository import AuthRepository
from backend.databases.connection import get_db
from sqlalchemy.orm import Session


router = APIRouter()

@router.post(
    "/session",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "User successfully logged in",
            "model": LoginResponse
        },
        400: {
            "description": "Validation error - Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Log in failed",
                        "endpoint": "/auth/session",
                        "method": "POST",
                        "errors": [
                            {
                                "field": "email",
                                "message": "Invalid email address",
                                },
                                {
                                "field": "password",
                                "message": "Invalid password"
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized login",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid credentials"
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error - Unexpected error occurred",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred: [error message]"
                    }
                }
            }
        }
    }
)
async def session(credentials: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    try:
        print("\n" + "="*50)
        print("POST /auth/session ENDPOINT - Received data:")
        print("="*50)
        print(f"Email: {credentials.email}")
        print(f"Password: {credentials.password}")
        print("="*50 + "\n")
        
        # Initialize repositories
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)
            
        # Get password hash from db
        result = await user_repo.get_by_email_with_password(credentials.email)

        if not result:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        user = result["user"]
        password_hash = result["password_hash"]

        if not verify_password(credentials.password, password_hash):
            raise HTTPException(status_code=401, detail= "Invalid credentials")
        
        session_id = await session_repo.create_session(user.id)

        return LoginResponse(
            session_id= session_id,
            user= user.user_to_user_response()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # If there is another exception, throw error 500 Internal Server Error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        ) 

@router.get(
    "/me",
    response_model = UserResponse,
    status_code= status.HTTP_200_OK,
    responses = {
        200: {
            "description": "Current authenticated user information retrieved successfully",
            "model": UserResponse,
            "content": {
                "application/json": {
                    "example": UserResponse
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid, missing, or expired session",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_header": {
                            "summary": "Missing Authorization header",
                            "value": {
                                "detail": "Authorization header is required"
                            }
                        },
                        "invalid_session": {
                            "summary": "Invalid or expired session",
                            "value": {
                                "detail": "Invalid or expired session"
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation Error - Missing or invalid Authorization header",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "missing",
                                "loc": ["header", "authorization"],
                                "msg": "Field required",
                                "input": None
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error - Unexpected error occurred",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred: [error message]"
                    }
                }
            }
        }
    }
) 
async def get_current_user(
    authorization: str = Header(...,description ="Session ID for authentication"),
    db:Session = Depends(get_db)
) -> UserResponse:
    try: 
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)

        user_response = await session_repo.get_user_by_session(authorization)
        if not user_response:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )
        
        await session_repo.update_last_activity(authorization)
        
        return user_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.post(
    "/logout",
    status_code = status.HTTP_204_NO_CONTENT,
    responses={
        204: {
            "description": "Session successfully terminated"
        },
        422: {
            "description": "Validation Error - Missing Authorization header",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "missing",
                                "loc": ["header", "authorization"],
                                "msg": "Field required",
                                "input": None
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An unexpected error occurred: [error message]"
                    }
                }
            }
        }
    }
)
async def logout(
    authorization: str = Header(...,description="Session ID to terminate"),
    db: Session = Depends(get_db)
) -> Response:
    try:
        session_repo = SessionRepository(db)
        await session_repo.delete_session(authorization)
       
        return Response(status_code = 204)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )