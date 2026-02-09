"""
Users Router
"""
from fastapi import APIRouter, HTTPException, status, Response, Depends
from backend.models.user import UserCreate, UserResponse, UserInsert
from backend.models.auth import AuthIdentityInsert
from backend.models.hash import hash_password
from backend.models.uuid import generate_uuid
from backend.models.auth import Provider
from backend.databases.user_repository import UserRepository
from backend.databases.auth_repository import AuthRepository
from backend.databases.connection import get_db
from sqlalchemy.orm import Session


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
    Creates both user record and authentication identity.
    """
    try:
        print("\n" + "="*50)
        print("USERS ENDPOINT - Received data:")
        print("="*50)
        print(f"Name: {user_data.name}")
        print(f"Email: {user_data.email}")
        print(f"Password: {user_data.password}")
        print(f"Contact Email: {user_data.contact_person_email}")
        print(f"Country Code: {user_data.contact_person_country_code}")
        print(f"Phone: {user_data.contact_person_phone_number}")
        print(f"Diversity Type: {user_data.diversity_type}")
        print("="*50 + "\n")
        
        # Initialize repositories
        user_repo = UserRepository(db)
        auth_repo = AuthRepository(db)
            
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
            **user_data.model_dump(exclude={'password'})
        )
        
        # Create auth identity for password authentication
        auth_identity = AuthIdentityInsert(
            user_id=database_user.id,  # Use the auto-generated user ID
            provider=Provider.PASSWORD,
            provider_user_id=None,  # Not needed for local auth
            password_hash=hashed_password
        )
        
        # Save user to database
        saved_user = await user_repo.create(database_user)
        
        # Save authentication identity
        await auth_repo.create(auth_identity)
        
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

