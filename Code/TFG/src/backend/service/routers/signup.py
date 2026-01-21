"""
Signup Router
"""
from fastapi import APIRouter, HTTPException, status, Response
from src.backend.models.user import UserCreate, UserResponse, User, UserRole
from src.backend.models.hash import hash_password

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def signup(user_data: UserCreate, response: Response):
    """
    Register a new user with email and password.
    Password is automatically hashed using Argon2
    """
    # Hash the password
    hashed_password = hash_password(user_data.password)
    
    # Generate the User model for the database
    database_user = User(
        **user_data.model_dump(exclude={'password'}),
        passwordHash=hashed_password
    )
    
    # db.save(database_user)
    
    # Return user response without passwordHash
    response.status_code = status.HTTP_200_OK
    return UserResponse(**database_user.model_dump(exclude={'passwordHash'})) 

