"""
Signup Router
"""
from fastapi import APIRouter, HTTPException, status, Response
from src.backend.models.user import UserCreate, UserResponse, User
from src.backend.models.hash import hash_password
from src.backend.databases.user_repository import UserRepository

router = APIRouter()

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
                        "endpoint": "/signup/",
                        "method": "POST",
                        "errors": [
                            {
                                "field": "email",
                                "message": "value is not a valid email address: An email address must have an @-sign.",
                                "type": "value_error",
                                "status": "invalid"
                                },
                                {
                                "field": "name",
                                "message": "Field is valid",
                                "type": "valid",
                                "status": "valid"
                                },
                                {
                                "field": "contact_person_email",
                                "message": "Field is valid",
                                "type": "valid",
                                "status": "valid"
                                },
                                {
                                "field": "contact_person_phone",
                                "message": "Field is valid",
                                "type": "valid",
                                "status": "valid"
                                },
                                {
                                "field": "diversity_type",
                                "message": "Field is valid",
                                "type": "valid",
                                "status": "valid"
                                },
                                {
                                "field": "password",
                                "message": "Field is valid",
                                "type": "valid",
                                "status": "valid"
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
async def signup(user_data: UserCreate, response: Response):
    """
    Register a new user with email and password.
    Password is automatically hashed using Argon2.
    """
    try:
        # Initialize repository
        repo = UserRepository()
            
        # Validate that the email does not exist in the database. 
        # If it exists, return with code 409
        if await repo.exists_user(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Generate the User model for the database
        database_user = User(
            **user_data.model_dump(exclude={'password'}),
            passwordHash=hashed_password
        )
        
        # Save user to database
        saved_user = await repo.create(database_user)
        
        # Return user response without passwordHash
        response.status_code = status.HTTP_200_OK
        return UserResponse(**saved_user.model_dump(exclude={'passwordHash'}))
        
    except HTTPException:
        # Re-raise HTTPExceptions (409 Conflict)
        raise
    except Exception as e:
        # If there is another exception, throw error 500 Internal Server Error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        ) 

