"""
Model Tests

Unit tests for domain models (User models).
"""

import pytest
from uuid import UUID
from datetime import datetime
from pydantic import ValidationError
from src.backend.models import (
    User, 
    UserBase, 
    UserCreate, 
    UserCreateOAuth,
    UserUpdate, 
    UserResponse,
    UserRole,
    UUIDType, 
    generate_uuid, 
    validate_uuid
)


class TestUserModel:
    """Test suite for UserBase model"""
    
    # Tests for the creation of UserBase Model    
    def test_user_base_with_only_required_field(self):
        """Test UserBase creation with only required field (email)"""
        user = UserBase(email="test@example.com")
        assert user.email == "test@example.com"
        assert user.name is None
        assert user.contact_person_email is None
        assert user.contact_person_phone is None
        assert user.diversity_type is None
    
    def test_user_base_with_all_fields(self, sample_user_base_data):
        """Test UserBase creation with all fields populated"""
        user = UserBase(**sample_user_base_data)
        assert user.email == sample_user_base_data["email"]
        assert user.name == sample_user_base_data["name"]
        assert user.contact_person_email == sample_user_base_data["contact_person_email"]
        # PhoneNumber formats as RFC 3966 (tel:+XX-XXX-XX-XX-XX), compare without formatting
        phone_normalized = sample_user_base_data["contact_person_phone"].replace("+", "").replace("-", "")
        stored_phone_normalized = str(user.contact_person_phone).replace("tel:", "").replace("+", "").replace("-", "")
        assert phone_normalized == stored_phone_normalized
        assert user.diversity_type == sample_user_base_data["diversity_type"]
    
    def test_user_base_with_optional_fields_none(self):
        """Test UserBase creation with optional fields explicitly set to None"""
        user = UserBase(
            email="test@example.com",
            name=None,
            contact_person_email=None,
            contact_person_phone=None,
            diversity_type=None
        )
        assert user.email == "test@example.com"
        assert user.name is None
        assert user.contact_person_email is None
        assert user.contact_person_phone is None
        assert user.diversity_type is None
    
    # email Validation tests for UserBase model
    
    def test_user_base_with_valid_email_formats(self):
        """Test UserBase accepts various valid email formats"""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user123@test-domain.com",
        ]
        for email in valid_emails:
            user = UserBase(email=email)
            assert user.email == email
    
    def test_user_base_without_email_fails(self):
        """Test UserBase creation fails without email (required field)"""
        with pytest.raises(ValidationError) as exc_info:
            UserBase()
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("email",)
        assert errors[0]["type"] == "missing"
    
    def test_user_base_with_invalid_email_format(self):
        """Test UserBase creation fails with invalid email format"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com",
        ]
        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                UserBase(email=invalid_email)
            errors = exc_info.value.errors()
            assert any("email" in str(error["loc"]) for error in errors)
    
    def test_user_base_with_empty_email(self):
        """Test UserBase creation fails with empty email"""
        with pytest.raises(ValidationError):
            UserBase(email="")
    
    # name validation tests
    
    def test_user_base_with_valid_name_min_length(self):
        """Test UserBase accepts name with minimum length (2 characters)"""
        user = UserBase(email="test@example.com", name="Al")
        assert user.name == "Al"
    
    def test_user_base_with_valid_name_long(self):
        """Test UserBase accepts long names"""
        long_name = "A" * 100
        user = UserBase(email="test@example.com", name=long_name)
        assert user.name == long_name
    
    def test_user_base_with_name_too_short(self):
        """Test UserBase creation fails with name shorter than 2 characters"""
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="test@example.com", name="A")
        errors = exc_info.value.errors()
        assert any("name" in str(error["loc"]) for error in errors)
        assert any("at least 2 characters" in str(error["msg"]).lower() for error in errors)
    
    def test_user_base_with_empty_name(self):
        """Test UserBase creation fails with empty name string"""
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="test@example.com", name="")
        errors = exc_info.value.errors()
        assert any("name" in str(error["loc"]) for error in errors)
    
    # contact_person_email validation tests
    
    def test_user_base_with_valid_contact_email(self):
        """Test UserBase accepts valid contact person email"""
        user = UserBase(
            email="user@example.com",
            contact_person_email="contact@example.com"
        )
        assert user.contact_person_email == "contact@example.com"
    
    def test_user_base_with_invalid_contact_email(self):
        """Test UserBase creation fails with invalid contact person email"""
        with pytest.raises(ValidationError) as exc_info:
            UserBase(
                email="user@example.com",
                contact_person_email="invalid-email"
            )
        errors = exc_info.value.errors()
        assert any("contact_person_email" in str(error["loc"]) for error in errors)
    
    def test_user_base_with_none_contact_email(self):
        """Test UserBase accepts None for contact_person_email"""
        user = UserBase(
            email="user@example.com",
            contact_person_email=None
        )
        assert user.contact_person_email is None
    
    # contact_person_phone validation tests
    
    def test_user_base_with_valid_phone_formats(self):
        """Test UserBase accepts various valid phone number formats"""
        valid_phones = [
            "+34600000000",
            "+442071234567",
        ]
        for phone in valid_phones:
            user = UserBase(
                email="test@example.com",
                contact_person_phone=phone
            )
            # PhoneNumber stores in RFC 3966 format, compare without formatting
            phone_str = str(user.contact_person_phone)
            assert "tel:" in phone_str
            phone_normalized = phone.replace("+", "").replace("-", "")
            stored_normalized = phone_str.replace("tel:", "").replace("+", "").replace("-", "")
            assert phone_normalized == stored_normalized
    
    def test_user_base_with_invalid_phone_format(self):
        """Test UserBase creation fails with invalid phone number"""
        invalid_phones = [
            "123",  # Too short
            "not-a-phone",
            "600000000",  # Missing country code
        ]
        for invalid_phone in invalid_phones:
            with pytest.raises(ValidationError) as exc_info:
                UserBase(
                    email="test@example.com",
                    contact_person_phone=invalid_phone
                )
            errors = exc_info.value.errors()
            assert any("contact_person_phone" in str(error["loc"]) for error in errors)
    
    def test_user_base_with_none_phone(self):
        """Test UserBase accepts None for contact_person_phone"""
        user = UserBase(
            email="test@example.com",
            contact_person_phone=None
        )
        assert user.contact_person_phone is None
    
    # diversity_type validation tests
    
    def test_user_base_with_diversity_type(self):
        """Test UserBase accepts diversity_type as string"""
        user = UserBase(
            email="test@example.com",
            diversity_type="visual"
        )
        assert user.diversity_type == "visual"
    
    def test_user_base_with_different_diversity_types(self):
        """Test UserBase accepts different diversity type values"""
        diversity_types = ["visual", "auditory", "motor", "cognitive", "none"]
        for diversity_type in diversity_types:
            user = UserBase(
                email="test@example.com",
                diversity_type=diversity_type
            )
            assert user.diversity_type == diversity_type
    
    def test_user_base_with_none_diversity_type(self):
        """Test UserBase accepts None for diversity_type"""
        user = UserBase(
            email="test@example.com",
            diversity_type=None
        )
        assert user.diversity_type is None
    
    # Incorrect data types tests
    
    def test_user_base_with_wrong_email_type(self):
        """Test UserBase creation fails with non-string email"""
        with pytest.raises(ValidationError):
            UserBase(email=12345)
    
    def test_user_base_with_wrong_name_type(self):
        """Test UserBase creation fails with non-string name"""
        with pytest.raises(ValidationError):
            UserBase(email="test@example.com", name=12345)
    
    def test_user_base_with_wrong_diversity_type_type(self):
        """Test UserBase creation fails with non-string diversity_type"""
        with pytest.raises(ValidationError):
            UserBase(email="test@example.com", diversity_type=12345)


class TestUserCreateModel:
    """Test suite for UserCreate model"""
    
    # Valid creation tests
    
    def test_user_create_with_all_fields(self, sample_user_create_data):
        """Test UserCreate with all fields populated"""
        user = UserCreate(**sample_user_create_data)
        assert user.email == sample_user_create_data["email"]
        assert user.name == sample_user_create_data["name"]
        assert user.password == sample_user_create_data["password"]
        assert user.contact_person_email == sample_user_create_data["contact_person_email"]
    
    def test_user_create_with_required_fields_only(self):
        """Test UserCreate with only required fields (email and password)"""
        user = UserCreate(email="test@example.com", password="securepass123")
        assert user.email == "test@example.com"
        assert user.password == "securepass123"
        assert user.name is None
        assert user.contact_person_email is None
    
    # Password validation tests
    
    def test_user_create_with_valid_password_min_length(self):
        """Test UserCreate accepts password with minimum length (8 characters)"""
        user = UserCreate(email="test@example.com", password="12345678")
        assert user.password == "12345678"
    
    def test_user_create_with_long_password(self):
        """Test UserCreate accepts long passwords"""
        long_password = "a" * 100
        user = UserCreate(email="test@example.com", password=long_password)
        assert user.password == long_password
    
    def test_user_create_without_password_fails(self):
        """Test UserCreate creation fails without password (required field)"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com")
        errors = exc_info.value.errors()
        assert any("password" in str(error["loc"]) for error in errors)
    
    def test_user_create_with_password_too_short(self):
        """Test UserCreate creation fails with password shorter than 8 characters"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="short")
        errors = exc_info.value.errors()
        assert any("password" in str(error["loc"]) for error in errors)
        assert any("at least 8 characters" in str(error["msg"]).lower() for error in errors)
    
    def test_user_create_with_empty_password(self):
        """Test UserCreate creation fails with empty password"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="")
        errors = exc_info.value.errors()
        assert any("password" in str(error["loc"]) for error in errors)
    
    # Inherited validation from UserBase
    
    def test_user_create_without_email_fails(self):
        """Test UserCreate creation fails without email"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(password="password123")
        errors = exc_info.value.errors()
        assert any("email" in str(error["loc"]) for error in errors)
    
    def test_user_create_with_invalid_email(self):
        """Test UserCreate creation fails with invalid email"""
        with pytest.raises(ValidationError):
            UserCreate(email="invalid-email", password="password123")
    
    def test_user_create_with_name_too_short(self):
        """Test UserCreate creation fails with name too short"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="password123",
                name="A"
            )


class TestUserCreateOAuthModel:
    """Test suite for UserCreateOAuth model"""
    
    # Valid creation tests
    
    def test_user_create_oauth_with_only_email(self):
        """Test UserCreateOAuth with only email (no password required)"""
        user = UserCreateOAuth(email="test@example.com")
        assert user.email == "test@example.com"
        assert user.name is None
        assert not hasattr(user, "password")
    
    def test_user_create_oauth_with_all_fields(self):
        """Test UserCreateOAuth with all optional fields"""
        user = UserCreateOAuth(
            email="oauth@example.com",
            name="OAuth User",
            contact_person_email="contact@example.com",
            contact_person_phone="+34600000000",
            diversity_type="visual"
        )
        assert user.email == "oauth@example.com"
        assert user.name == "OAuth User"
        assert user.contact_person_email == "contact@example.com"
    
    # Validation tests
    
    def test_user_create_oauth_without_email_fails(self):
        """Test UserCreateOAuth creation fails without email"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreateOAuth()
        errors = exc_info.value.errors()
        assert any("email" in str(error["loc"]) for error in errors)
    
    def test_user_create_oauth_with_invalid_email_fails(self):
        """Test UserCreateOAuth creation fails with invalid email"""
        with pytest.raises(ValidationError):
            UserCreateOAuth(email="not-an-email")
    
    def test_user_create_oauth_does_not_accept_password(self):
        """Test UserCreateOAuth ignores password field (not in schema)"""
        user = UserCreateOAuth(
            email="test@example.com",
            password="should_be_ignored"
        )
        # Password should be ignored since it's not in the schema
        assert not hasattr(user, "password")


class TestUserUpdateModel:
    """Test suite for UserUpdate model"""
    
    # Valid update tests
    
    def test_user_update_with_all_fields_none(self):
        """Test UserUpdate can be created with all fields as None"""
        user_update = UserUpdate()
        assert user_update.email is None
        assert user_update.name is None
        assert user_update.password is None
        assert user_update.contact_person_email is None
        assert user_update.contact_person_phone is None
        assert user_update.diversity_type is None
        assert user_update.role is None
        assert user_update.email_verified is None
        assert user_update.settings is None
    
    def test_user_update_with_partial_fields(self, sample_user_update_data):
        """Test UserUpdate with only some fields"""
        user_update = UserUpdate(**sample_user_update_data)
        assert user_update.email == sample_user_update_data["email"]
        assert user_update.name == sample_user_update_data["name"]
        assert user_update.password is None
    
    def test_user_update_with_all_fields(self):
        """Test UserUpdate with all fields populated"""
        user_update = UserUpdate(
            email="updated@example.com",
            name="Updated Name",
            password="newpassword123",
            contact_person_email="newcontact@example.com",
            contact_person_phone="+34611111111",
            diversity_type="motor",
            role=UserRole.ADMIN,
            email_verified=True,
            settings={"theme": "dark"}
        )
        assert user_update.email == "updated@example.com"
        assert user_update.name == "Updated Name"
        assert user_update.role == UserRole.ADMIN
        assert user_update.email_verified is True
        assert user_update.settings == {"theme": "dark"}
    
    # Validation tests
    
    def test_user_update_with_invalid_email(self):
        """Test UserUpdate creation fails with invalid email"""
        with pytest.raises(ValidationError):
            UserUpdate(email="invalid-email")
    
    def test_user_update_with_password_too_short(self):
        """Test UserUpdate creation fails with password shorter than 8 characters"""
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(password="short")
        errors = exc_info.value.errors()
        assert any("password" in str(error["loc"]) for error in errors)
    
    def test_user_update_with_name_too_short(self):
        """Test UserUpdate creation fails with name shorter than 2 characters"""
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(name="A")
        errors = exc_info.value.errors()
        assert any("name" in str(error["loc"]) for error in errors)
    
    def test_user_update_with_invalid_role(self):
        """Test UserUpdate creation fails with invalid role"""
        with pytest.raises(ValidationError):
            UserUpdate(role="invalid_role")
    
    def test_user_update_with_valid_role(self):
        """Test UserUpdate accepts valid UserRole enum"""
        user_update = UserUpdate(role=UserRole.MODERATOR)
        assert user_update.role == UserRole.MODERATOR
    
    def test_user_update_email_verified_boolean(self):
        """Test UserUpdate accepts boolean for email_verified"""
        user_update_true = UserUpdate(email_verified=True)
        user_update_false = UserUpdate(email_verified=False)
        assert user_update_true.email_verified is True
        assert user_update_false.email_verified is False
    
    def test_user_update_settings_as_dict(self):
        """Test UserUpdate accepts dictionary for settings"""
        settings = {"language": "en", "notifications": {"email": True}}
        user_update = UserUpdate(settings=settings)
        assert user_update.settings == settings


class TestCompleteUserModel:
    """Test suite for User model (complete database representation)"""
    
    # Valid creation tests
    
    def test_user_with_required_fields_only(self):
        """Test User creation with only required field (email)"""
        user = User(email="test@example.com")
        assert user.email == "test@example.com"
        assert user.name is None
        assert isinstance(user.id, UUID)
        assert user.passwordHash is None
        assert user.role == UserRole.USER
        assert isinstance(user.created_at, datetime)
        assert user.email_verified is False
        assert user.settings == {}
    
    def test_user_with_all_fields(self):
        """Test User creation with all fields populated"""
        test_id = generate_uuid()
        test_datetime = datetime.now()
        user = User(
            id=test_id,
            email="complete@example.com",
            name="Complete User",
            passwordHash="$2b$12$hashed_password",
            contact_person_email="contact@example.com",
            contact_person_phone="+34600000000",
            diversity_type="visual",
            role=UserRole.ADMIN,
            created_at=test_datetime,
            email_verified=True,
            settings={"theme": "dark", "language": "en"}
        )
        assert user.id == test_id
        assert user.email == "complete@example.com"
        assert user.name == "Complete User"
        assert user.passwordHash == "$2b$12$hashed_password"
        assert user.role == UserRole.ADMIN
        assert user.created_at == test_datetime
        assert user.email_verified is True
        assert user.settings == {"theme": "dark", "language": "en"}
    
    # Default values tests
    
    def test_user_generates_unique_id(self):
        """Test User generates unique UUIDs for each instance"""
        user1 = User(email="user1@example.com")
        user2 = User(email="user2@example.com")
        assert user1.id != user2.id
        assert isinstance(user1.id, UUID)
        assert isinstance(user2.id, UUID)
    
    def test_user_default_role_is_user(self):
        """Test User default role is USER"""
        user = User(email="test@example.com")
        assert user.role == UserRole.USER
    
    def test_user_default_email_verified_is_false(self):
        """Test User default email_verified is False"""
        user = User(email="test@example.com")
        assert user.email_verified is False
    
    def test_user_default_settings_is_empty_dict(self):
        """Test User default settings is empty dictionary"""
        user = User(email="test@example.com")
        assert user.settings == {}
        assert isinstance(user.settings, dict)
    
    def test_user_created_at_auto_generated(self):
        """Test User created_at is automatically generated"""
        before = datetime.now()
        user = User(email="test@example.com")
        after = datetime.now()
        assert before <= user.created_at <= after
        assert isinstance(user.created_at, datetime)
    
    # OAuth user tests
    
    def test_user_for_oauth_without_password_hash(self):
        """Test User can be created without passwordHash for OAuth users"""
        user = User(
            email="oauth@example.com",
            name="OAuth User",
            passwordHash=None
        )
        assert user.passwordHash is None
        assert user.email == "oauth@example.com"
    
    def test_user_for_traditional_auth_with_password_hash(self):
        """Test User with passwordHash for traditional authentication"""
        user = User(
            email="traditional@example.com",
            passwordHash="$2b$12$hashed_password"
        )
        assert user.passwordHash == "$2b$12$hashed_password"
    
    # Validation tests
    
    def test_user_without_email_fails(self):
        """Test User creation fails without email"""
        with pytest.raises(ValidationError) as exc_info:
            User()
        errors = exc_info.value.errors()
        assert any("email" in str(error["loc"]) for error in errors)
    
    def test_user_with_invalid_email_fails(self):
        """Test User creation fails with invalid email"""
        with pytest.raises(ValidationError):
            User(email="not-an-email")
    
    def test_user_with_invalid_role(self):
        """Test User creation fails with invalid role"""
        with pytest.raises(ValidationError):
            User(email="test@example.com", role="invalid_role")
    
    def test_user_with_wrong_type_email_verified(self):
        """Test User creation fails with wrong type for email_verified"""
        with pytest.raises(ValidationError):
            User(email="test@example.com", email_verified="not_a_boolean")
    
    def test_user_with_wrong_type_settings(self):
        """Test User creation fails with wrong type for settings"""
        with pytest.raises(ValidationError):
            User(email="test@example.com", settings="not_a_dict")


class TestUserResponseModel:
    """Test suite for UserResponse model"""
    
    # Valid creation tests
    
    def test_user_response_with_all_fields(self):
        """Test UserResponse creation with all required fields"""
        test_id = generate_uuid()
        test_datetime = datetime.now()
        user_response = UserResponse(
            id=test_id,
            email="response@example.com",
            name="Response User",
            contact_person_email="contact@example.com",
            contact_person_phone="+34600000000",
            diversity_type="visual",
            role=UserRole.USER,
            created_at=test_datetime,
            email_verified=True,
            settings={"theme": "dark"}
        )
        assert user_response.id == test_id
        assert user_response.email == "response@example.com"
        assert user_response.name == "Response User"
        assert user_response.role == UserRole.USER
        assert user_response.created_at == test_datetime
        assert user_response.email_verified is True
        assert user_response.settings == {"theme": "dark"}
    
    def test_user_response_does_not_have_password_hash(self):
        """Test UserResponse does not expose passwordHash field"""
        test_id = generate_uuid()
        user_response = UserResponse(
            id=test_id,
            email="test@example.com",
            name="Test User",
            contact_person_email=None,
            contact_person_phone=None,
            diversity_type=None,
            role=UserRole.USER,
            created_at=datetime.now(),
            email_verified=False,
            settings={}
        )
        assert not hasattr(user_response, "passwordHash")
    
    def test_user_response_from_user_model(self):
        """Test creating UserResponse from User model (excluding sensitive data)"""
        user = User(
            email="user@example.com",
            name="Test User",
            passwordHash="$2b$12$sensitive_hash"
        )
        # Create response by excluding passwordHash
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            contact_person_email=user.contact_person_email,
            contact_person_phone=user.contact_person_phone,
            diversity_type=user.diversity_type,
            role=user.role,
            created_at=user.created_at,
            email_verified=user.email_verified,
            settings=user.settings
        )
        assert user_response.email == user.email
        assert user_response.id == user.id
        assert not hasattr(user_response, "passwordHash")
    
    # Validation tests
    
    def test_user_response_requires_id(self):
        """Test UserResponse creation fails without id"""
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(
                email="test@example.com",
                name="Test User",
                role=UserRole.USER,
                created_at=datetime.now(),
                email_verified=False,
                settings={}
            )
        errors = exc_info.value.errors()
        assert any("id" in str(error["loc"]) for error in errors)
    
    def test_user_response_requires_email(self):
        """Test UserResponse creation fails without email"""
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(
                id=generate_uuid(),
                name="Test User",
                role=UserRole.USER,
                created_at=datetime.now(),
                email_verified=False,
                settings={}
            )
        errors = exc_info.value.errors()
        assert any("email" in str(error["loc"]) for error in errors)
    
    def test_user_response_requires_name(self):
        """Test UserResponse creation fails without name"""
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(
                id=generate_uuid(),
                email="test@example.com",
                role=UserRole.USER,
                created_at=datetime.now(),
                email_verified=False,
                settings={}
            )
        errors = exc_info.value.errors()
        assert any("name" in str(error["loc"]) for error in errors)
    
    def test_user_response_with_optional_fields_none(self):
        """Test UserResponse accepts None for optional fields"""
        user_response = UserResponse(
            id=generate_uuid(),
            email="test@example.com",
            name="Test User",
            contact_person_email=None,
            contact_person_phone=None,
            diversity_type=None,
            role=UserRole.USER,
            created_at=datetime.now(),
            email_verified=False,
            settings={}
        )
        assert user_response.contact_person_email is None
        assert user_response.contact_person_phone is None
        assert user_response.diversity_type is None
    


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
