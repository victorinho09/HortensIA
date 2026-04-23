"""
Users Router
"""
import logging

from backend.databases.session_repository import SessionRepository
from backend.service.dependencies import get_current_user_from_session
from fastapi import APIRouter, HTTPException, status, Response, Depends, Header
from backend.models.user import UserCreate, UserResponse, UserInsert, UserUpdate,PasswordChange
from backend.utils.hash import hash_password, verify_password
from backend.utils.uuid import validate_uuid
from backend.databases.user_repository import UserRepository
from backend.databases.connection import get_db
from sqlalchemy.orm import Session


router = APIRouter()

logger = logging.getLogger(__name__)

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "User successfully registered",
            "model": UserResponse
        },
        400: {
            "description": "Validation error - Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Validation failed",
                        "endpoint": "/users/",
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
        409: {
            "description": "Conflict - User with this email already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User with this email already exists"
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
async def users(user_data: UserCreate, response: Response, db: Session = Depends(get_db)):
    """
    Register a new user with email and password.
    Password is automatically hashed using Argon2.
    Stores the user record with a hashed password.
    """
    try:
        logger.debug("POST /users/ - name=%s email=%s diversity_type=%s",
                     user_data.name, user_data.email, user_data.diversity_type)
        
        # Initialize repositories
        user_repo = UserRepository(db)
            
        # Validate that the email does not exist in the database. 
        # If it exists, return with code 409
        if await user_repo.exists_user(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Generate the User model for the database (UUID auto-generated)
        database_user = UserInsert(
            **user_data.model_dump(exclude={'password'}),
            passwordHash=hashed_password
        )
        
        # Save user to database
        saved_user = await user_repo.create(database_user)
        
        # Return user response without passwordHash
        response.status_code = status.HTTP_200_OK
        return saved_user.user_to_user_response()
        
    except HTTPException:
        # Re-raise HTTPExceptions (409 Conflict)
        raise
    except Exception as e:
        # If there is another exception, throw error 500 Internal Server Error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        ) 
    
@router.patch(
    "/me",
    response_model= UserResponse,
    status_code=200,
    responses={
        200: {
            "description": "user profile updated successfully",
            "model": UserResponse
        },
        400: {
            "description": "Validation error - Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Validation failed",
                        "endpoint": "/users/me",
                        "method": "PATCH",
                        "errors": [
                            {
                                "field": "name",
                                "message": "Field is too short",
                                "type": "value_error",
                                "status": "invalid"
                            }
                        ]
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or expired session",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or expired session"}
                } 
            }
        },
        404: {
            "description": "Not Found - User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "An unexpected error occurred"}
                }
            }
        }
    }
)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user_from_session), #Validates the UUID format of sessionID
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Update the current user's profile
    Only provided fields will be updated
    Password will be hashed if changed
    """
    try:
        update_data = user_update.model_dump(exclude_unset=True)
        
        user_repo = UserRepository(db)
        updated_user = await user_repo.update(current_user.id, update_data)

        if not updated_user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return updated_user.user_to_user_response()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.patch(
    "/me/password",
    status_code = 200,
    responses={
        200: {
            "description": "Password changed successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Password changed successfully"}
                }
            }
        },
        400: {
            "description": "Invalid current password",
            "content": {
                "application/json": {
                    "example": {"detail": "Current password is incorrect"}
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or expired session",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or expired session"}
                } 
            }
        },
        404: {
            "description": "Not Found - User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "An unexpected error occurred"}
                }
            }
        }
    }
)
async def change_password(
    password_change: PasswordChange,
    current_user: UserResponse = Depends(get_current_user_from_session),
    db: Session = Depends(get_db)
):
    """
    Change the current user's password
    Requires current password for verification
    """
    try:
        user_repo = UserRepository(db)
        user_with_password = await user_repo.get_by_email_with_password(current_user.email)

        if not user_with_password:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        current_hash = user_with_password["password_hash"]
        if not verify_password(password_change.current_password,current_hash):
            raise HTTPException(
                status_code= 400,
                detail= "Current password is incorrect"
            )
        
        new_hash = hash_password(password_change.new_password)
        await user_repo.update_password(current_user.id,new_hash)

        return {"message" : "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = f"An unexpected error ocurred: {str(e)}"
        )

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {
            "description": "Account deleted successfully"
        },
        401: {
            "description": "Unauthorized - Invalid or expired session",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or expired session"}
                }
            }
        },
        404: {
            "description": "Not Found - User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "An unexpected error occurred"}
                }
            }
        }
    }
)
async def delete_current_user(
    current_user: UserResponse = Depends(get_current_user_from_session),
    db: Session = Depends(get_db)
):
    """
    Delete the current user's account and all associated data.
    """
    try:
        user_repo = UserRepository(db)
        deleted = await user_repo.delete(current_user.id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )