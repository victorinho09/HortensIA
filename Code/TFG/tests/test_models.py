"""
Model Tests

Unit tests for domain models (User, UUID, etc.)
"""

import pytest
from uuid import UUID
from pydantic import ValidationError
from src.backend.models import User, UserCreate, UserUpdate, UUIDType, generate_uuid, validate_uuid


class TestUUIDModel:
    """Test suite for UUID utilities"""
    
    def test_generate_uuid_returns_valid_uuid(self):
        """Test that generate_uuid creates valid UUIDs"""
        uuid = generate_uuid()
        assert isinstance(uuid, UUID)
    
    def test_generate_uuid_creates_unique_ids(self):
        """Test that each generated UUID is unique"""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        assert uuid1 != uuid2
    
    def test_validate_uuid_with_valid_string(self):
        """Test UUID validation with valid string"""
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"
        result = validate_uuid(uuid_str)
        assert isinstance(result, UUID)
        assert str(result) == uuid_str
    
    def test_validate_uuid_with_uuid_object(self):
        """Test UUID validation with UUID object"""
        uuid_obj = UUID("123e4567-e89b-12d3-a456-426614174000")
        result = validate_uuid(uuid_obj)
        assert result == uuid_obj
    
    def test_validate_uuid_with_invalid_string(self):
        """Test UUID validation fails with invalid string"""
        with pytest.raises(ValueError):
            validate_uuid("not-a-uuid")


class TestUserModel:
    """Test suite for User domain models"""
    
    def test_user_create_with_valid_data(self, sample_user_create_data):
        """Test creating user with valid data"""
        user = UserCreate(**sample_user_create_data)
        assert user.email == sample_user_create_data["email"]
        assert user.full_name == sample_user_create_data["full_name"]
        assert user.password == sample_user_create_data["password"]
    
    def test_user_create_without_password_fails(self, sample_user_create_data):
        """Test that user creation without password fails"""
        data = sample_user_create_data.copy()
        del data["password"]
        with pytest.raises(ValidationError):
            UserCreate(**data)
    
    def test_user_create_with_short_password_fails(self, sample_user_create_data):
        """Test that password must be at least 8 characters"""
        data = sample_user_create_data.copy()
        data["password"] = "short"
        with pytest.raises(ValidationError):
            UserCreate(**data)
    
    def test_user_create_with_invalid_email_fails(self, sample_user_create_data):
        """Test that invalid email format fails"""
        data = sample_user_create_data.copy()
        data["email"] = "not-an-email"
        with pytest.raises(ValidationError):
            UserCreate(**data)
    
    def test_user_update_all_fields_optional(self):
        """Test that all UserUpdate fields are optional"""
        user_update = UserUpdate()
        assert user_update.email is None
        assert user_update.full_name is None
        assert user_update.password is None
    
    def test_user_update_partial_data(self, sample_user_update_data):
        """Test updating only some fields"""
        user_update = UserUpdate(**sample_user_update_data)
        assert user_update.email == sample_user_update_data["email"]
        assert user_update.full_name == sample_user_update_data["full_name"]
        assert user_update.password is None
    
    def test_user_model_generates_id(self, sample_user_data):
        """Test that User model generates UUID automatically"""
        data = sample_user_data.copy()
        
        user = User(**data)
        assert isinstance(user.id, UUID)
    
    def test_user_model_accepts_custom_id(self, sample_user_data):
        """Test that User model accepts custom UUID"""
        data = sample_user_data.copy()
        custom_id = generate_uuid()
        data["id"] = custom_id        
        user = User(**data)
        assert user.id == custom_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
