"""
Password Hashing Module

Provides secure password hashing and verification using Argon2.
Argon2 is the winner of the Password Hashing Competition and is 
recommended for password storage.
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError


# Initialize the password hasher with secure defaults
# These parameters are recommended by OWASP
_password_hasher = PasswordHasher(
    time_cost=2,        # Number of iterations
    memory_cost=65536,  # Memory usage in KiB (64 MB)
    parallelism=4,      # Number of parallel threads
    hash_len=32,        # Length of the hash in bytes
    salt_len=16         # Length of the salt in bytes
)


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string in Argon2 format
        
    Raises:
        TypeError: If password is not a string
        ValueError: If password is empty
        
    Example:
        >>> hashed = hash_password("mySecurePassword123")
        >>> print(hashed)
        $argon2id$v=19$m=65536,t=2,p=4$...
    """
    if not isinstance(password, str):
        raise TypeError("Password must be a string")
    
    if not password:
        raise ValueError("Password cannot be empty")
    
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        password_hash: Hashed password to verify against
        
    Returns:
        True if password matches the hash, False otherwise
        
    Example:
        >>> hashed = hash_password("myPassword")
        >>> verify_password("myPassword", hashed)
        True
        >>> verify_password("wrongPassword", hashed)
        False
    """
    try:
        _password_hasher.verify(password_hash, password)
        return True
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def needs_rehash(password_hash: str) -> bool:
    """
    Check if a password hash needs to be rehashed.
    
    This is useful when you update your hashing parameters and want to
    rehash existing passwords on next login.
    
    Args:
        password_hash: Hashed password to check
        
    Returns:
        True if the hash needs to be updated, False otherwise
        
    Example:
        >>> hashed = hash_password("myPassword")
        >>> needs_rehash(hashed)
        False
    """
    try:
        return _password_hasher.check_needs_rehash(password_hash)
    except (InvalidHashError, ValueError):
        # If hash is invalid, it definitely needs rehashing
        return True
