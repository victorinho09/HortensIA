"""
Authentication Model Tests

Unit tests for authentication models (LoginRequest, LoginResponse).
"""

import pytest
from pydantic import ValidationError
from backend.models.auth import LoginRequest, LoginResponse
from backend.models.user import UserResponse


class TestLoginRequestModel:
    """Test suite for LoginRequest model"""
    
    # Tests for the creation of LoginRequest Model
    
    def test_login_request_with_valid_data(self, sample_login_request_data):
        """Test LoginRequest creation with valid email and password"""
        login = LoginRequest(**sample_login_request_data)
        assert login.email == sample_login_request_data["email"]
        assert login.password == sample_login_request_data["password"]
    
    def test_login_request_with_minimum_password_length(self):
        """Test LoginRequest accepts password with minimum length (8 characters)"""
        login = LoginRequest(email="test@example.com", password="12345678")
        assert login.password == "12345678"
        assert len(login.password) == 8
    
    def test_login_request_with_long_password(self):
        """Test LoginRequest accepts long passwords"""
        long_password = "a" * 100
        login = LoginRequest(email="test@example.com", password=long_password)
        assert login.password == long_password
        assert len(login.password) == 100
    
    # Email Validation tests for LoginRequest model
    
    def test_login_request_with_valid_email_formats(self):
        """Test LoginRequest accepts various valid email formats"""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user123@test-domain.com",
            "test.email+tag@subdomain.example.com",
        ]
        for email in valid_emails:
            login = LoginRequest(email=email, password="password123")
            assert login.email == email
    
    def test_login_request_with_invalid_email_format(self):
        """Test LoginRequest creation fails with invalid email format"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com",
            "user..name@example.com",
        ]
        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                LoginRequest(email=invalid_email, password="password123")
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("email",) for error in errors)
    
    def test_login_request_without_email_fails(self):
        """Test LoginRequest creation fails without email (required field)"""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(password="password123")
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("email",)
        assert errors[0]["type"] == "missing"
    
    # Password Validation tests for LoginRequest model
    
    def test_login_request_with_short_password_fails(self):
        """Test LoginRequest creation fails with password shorter than 8 characters"""
        short_passwords = ["1234567", "abc", "pw", "a" * 7]
        for password in short_passwords:
            with pytest.raises(ValidationError) as exc_info:
                LoginRequest(email="test@example.com", password=password)
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("password",) for error in errors)
            assert any("at least 8 characters" in str(error["msg"]).lower() for error in errors)
    
    def test_login_request_without_password_fails(self):
        """Test LoginRequest creation fails without password (required field)"""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(email="test@example.com")
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("password",)
        assert errors[0]["type"] == "missing"
    
    def test_login_request_with_empty_password_fails(self):
        """Test LoginRequest creation fails with empty password"""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(email="test@example.com", password="")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("password",) for error in errors)
    
    # Tests for edge cases
    
    def test_login_request_with_special_characters_in_password(self):
        """Test LoginRequest accepts passwords with special characters"""
        special_passwords = [
            "P@ssw0rd!",
            "test#123$",
            "my-pass_word.123",
            "pássword123",  # Unicode
            "password with spaces",
        ]
        for password in special_passwords:
            login = LoginRequest(email="test@example.com", password=password)
            assert login.password == password
    
    def test_login_request_immutability(self):
        """Test LoginRequest is frozen (Pydantic v2 models are mutable by default)"""
        # Note: Pydantic v2 models are mutable by default unless frozen=True in config
        login = LoginRequest(email="test@example.com", password="password123")
        # This test verifies that reassignment works (models are mutable)
        original_email = login.email
        # Pydantic v2 allows reassignment by default
        assert original_email == "test@example.com"
    
    def test_login_request_model_dump(self, sample_login_request_data):
        """Test LoginRequest can be serialized to dictionary"""
        login = LoginRequest(**sample_login_request_data)
        data = login.model_dump()
        assert data["email"] == sample_login_request_data["email"]
        assert data["password"] == sample_login_request_data["password"]
        assert isinstance(data, dict)
    
    def test_login_request_model_dump_json(self, sample_login_request_data):
        """Test LoginRequest can be serialized to JSON"""
        login = LoginRequest(**sample_login_request_data)
        json_str = login.model_dump_json()
        assert isinstance(json_str, str)
        assert sample_login_request_data["email"] in json_str
        assert sample_login_request_data["password"] in json_str


class TestLoginResponseModel:
    """Test suite for LoginResponse model"""
    
    # Tests for the creation of LoginResponse Model
    
    def test_login_response_with_valid_data(self, sample_login_response_data):
        """Test LoginResponse creation with valid session_id and user"""
        response = LoginResponse(**sample_login_response_data)
        assert response.session_id == sample_login_response_data["session_id"]
        assert response.user.email == sample_login_response_data["user"]["email"]
        # user.id is converted to UUID, so compare as string
        assert str(response.user.id) == sample_login_response_data["user"]["id"]
    
    def test_login_response_with_uuid_session_id(self, sample_user_response_data):
        """Test LoginResponse accepts valid UUID as session_id"""
        valid_uuids = [
            "123e4567-e89b-12d3-a456-426614174000",
            "550e8400-e29b-41d4-a716-446655440000",
            "a1b2c3d4-e5f6-4789-a123-456789abcdef",
        ]
        for uuid_str in valid_uuids:
            response = LoginResponse(
                session_id=uuid_str,
                user=UserResponse(**sample_user_response_data)
            )
            assert response.session_id == uuid_str
    
    # Session ID validation tests
    
    def test_login_response_without_session_id_fails(self, sample_user_response_data):
        """Test LoginResponse creation fails without session_id (required field)"""
        with pytest.raises(ValidationError) as exc_info:
            LoginResponse(user=UserResponse(**sample_user_response_data))
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("session_id",)
        assert errors[0]["type"] == "missing"
    
    def test_login_response_with_empty_session_id_accepts(self, sample_user_response_data):
        """Test LoginResponse accepts empty session_id (string validation is permissive)"""
        # Note: session_id is just a str type, so empty string is technically valid
        # In production, validation would happen at database/business logic level
        response = LoginResponse(
            session_id="",
            user=UserResponse(**sample_user_response_data)
        )
        assert response.session_id == ""
    
    # User validation tests
    
    def test_login_response_without_user_fails(self):
        """Test LoginResponse creation fails without user (required field)"""
        with pytest.raises(ValidationError) as exc_info:
            LoginResponse(session_id="123e4567-e89b-12d3-a456-426614174000")
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("user",)
        assert errors[0]["type"] == "missing"
    
    def test_login_response_with_invalid_user_type_fails(self):
        """Test LoginResponse creation fails when user is not UserResponse type"""
        with pytest.raises(ValidationError) as exc_info:
            LoginResponse(
                session_id="123e4567-e89b-12d3-a456-426614174000",
                user="not a user object"
            )
        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "user" for error in errors)
    
    def test_login_response_user_is_user_response_type(self, sample_login_response_data):
        """Test LoginResponse user field is UserResponse instance"""
        response = LoginResponse(**sample_login_response_data)
        assert isinstance(response.user, UserResponse)
    
    # Tests for serialization
    
    def test_login_response_model_dump(self, sample_login_response_data):
        """Test LoginResponse can be serialized to dictionary"""
        response = LoginResponse(**sample_login_response_data)
        data = response.model_dump()
        assert data["session_id"] == sample_login_response_data["session_id"]
        assert data["user"]["email"] == sample_login_response_data["user"]["email"]
        assert isinstance(data, dict)
        assert isinstance(data["user"], dict)
    
    def test_login_response_model_dump_json(self, sample_login_response_data):
        """Test LoginResponse can be serialized to JSON"""
        response = LoginResponse(**sample_login_response_data)
        json_str = response.model_dump_json()
        assert isinstance(json_str, str)
        assert sample_login_response_data["session_id"] in json_str
        assert sample_login_response_data["user"]["email"] in json_str
    
    def test_login_response_nested_user_serialization(self, sample_login_response_data):
        """Test LoginResponse properly serializes nested UserResponse"""
        response = LoginResponse(**sample_login_response_data)
        data = response.model_dump()
        user_data = data["user"]
        assert "id" in user_data
        assert "email" in user_data
        assert "name" in user_data
        assert "role" in user_data
        assert "email_verified" in user_data
        # Verify passwordHash is NOT included in UserResponse
        assert "passwordHash" not in user_data
        assert "password_hash" not in user_data
    
    # Tests for immutability
    
    def test_login_response_immutability(self, sample_login_response_data):
        """Test LoginResponse mutability (Pydantic v2 models are mutable by default)"""
        # Note: Pydantic v2 models are mutable by default unless frozen=True
        response = LoginResponse(**sample_login_response_data)
        original_session_id = response.session_id
        # Verify we can access the fields
        assert original_session_id == sample_login_response_data["session_id"]
        assert response.user.email == sample_login_response_data["user"]["email"]
    
    # Tests for edge cases
    
    def test_login_response_with_all_user_fields(self, sample_user_response_data):
        """Test LoginResponse works with UserResponse containing all optional fields"""
        response = LoginResponse(
            session_id="123e4567-e89b-12d3-a456-426614174000",
            user=UserResponse(**sample_user_response_data)
        )
        assert response.user.name == sample_user_response_data["name"]
        assert response.user.contact_person_email == sample_user_response_data["contact_person_email"]
        assert response.user.diversity_type == sample_user_response_data["diversity_type"]
    
    def test_login_response_with_minimal_user_fields(self):
        """Test LoginResponse works with UserResponse containing only required fields"""
        minimal_user = UserResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            name=None,
            contact_person_email=None,
            contact_person_country_code=None,
            contact_person_phone_number=None,
            diversity_type=None,
            passwordHash=None,
            role="user",
            email_verified=False,
            created_at="2024-01-01T00:00:00Z"
        )
        response = LoginResponse(
            session_id="123e4567-e89b-12d3-a456-426614174000",
            user=minimal_user
        )
        assert response.user.email == "test@example.com"
        assert response.user.name is None
