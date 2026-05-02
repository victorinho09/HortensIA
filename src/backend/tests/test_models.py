"""
Model Tests

Unit tests for domain models (User models).
"""

import pytest
from uuid import UUID
from datetime import datetime
from pydantic import ValidationError
from backend.models import (
    User, 
    UserBase, 
    UserCreate, 
    UserUpdate,
    PasswordChange,
    UserInsert,
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
        assert user.contact_person_country_code is None
        assert user.contact_person_phone_number is None
        assert user.diversity_type is None
    
    def test_user_base_with_all_fields(self, sample_user_base_data):
        """Test UserBase creation with all fields populated"""
        user = UserBase(**sample_user_base_data)
        assert user.email == sample_user_base_data["email"]
        assert user.name == sample_user_base_data["name"]
        assert user.contact_person_email == sample_user_base_data["contact_person_email"]
        assert user.contact_person_country_code == sample_user_base_data["contact_person_country_code"]
        assert user.contact_person_phone_number == sample_user_base_data["contact_person_phone_number"]
        assert user.diversity_type == sample_user_base_data["diversity_type"]
    
    def test_user_base_with_optional_fields_none(self):
        """Test UserBase creation with optional fields explicitly set to None"""
        user = UserBase(
            email="test@example.com",
            name=None,
            contact_person_email=None,
            contact_person_country_code=None,
            contact_person_phone_number=None,
            diversity_type=None
        )
        assert user.email == "test@example.com"
        assert user.name is None
        assert user.contact_person_email is None
        assert user.contact_person_country_code is None
        assert user.contact_person_phone_number is None
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
    
    # contact_person_country_code and contact_person_phone_number validation tests
    
    def test_user_base_with_valid_phone_fields(self):
        """Test UserBase accepts valid phone country code and number"""
        user = UserBase(
            email="test@example.com",
            contact_person_country_code="34",
            contact_person_phone_number="600000000"
        )
        assert user.contact_person_country_code == "34"
        assert user.contact_person_phone_number == "600000000"
    
    def test_user_base_with_none_phone_fields(self):
        """Test UserBase accepts None for phone fields"""
        user = UserBase(
            email="test@example.com",
            contact_person_country_code=None,
            contact_person_phone_number=None
        )
        assert user.contact_person_country_code is None
        assert user.contact_person_phone_number is None
    
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


class TestUserUpdateModel:
    """Test suite for UserUpdate model"""
    
    # Valid update tests
    
    def test_user_update_with_all_fields_none(self):
        """Test UserUpdate can be created with all fields as None"""
        user_update = UserUpdate()
        assert user_update.email is None
        assert user_update.name is None
        assert user_update.contact_person_email is None
        assert user_update.contact_person_country_code is None
        assert user_update.contact_person_phone_number is None
        assert user_update.diversity_type is None
        assert user_update.role is None
        assert user_update.email_verified is None
    
    def test_user_update_with_partial_fields(self, sample_user_update_data):
        """Test UserUpdate with only some fields"""
        user_update = UserUpdate(**sample_user_update_data)
        assert user_update.email == sample_user_update_data["email"]
        assert user_update.name == sample_user_update_data["name"]
    
    def test_user_update_with_all_fields(self):
        """Test UserUpdate with all fields populated"""
        user_update = UserUpdate(
            email="updated@example.com",
            name="Updated Name",
            contact_person_email="newcontact@example.com",
            contact_person_country_code="34",
            contact_person_phone_number="611111111",
            diversity_type="motor",
            role=UserRole.ADMIN,
            email_verified=True
        )
        assert user_update.email == "updated@example.com"
        assert user_update.name == "Updated Name"
        assert user_update.contact_person_country_code == "34"
        assert user_update.contact_person_phone_number == "611111111"
        assert user_update.role == UserRole.ADMIN
        assert user_update.email_verified is True
    
    # Validation tests
    
    def test_user_update_with_invalid_email(self):
        """Test UserUpdate creation fails with invalid email"""
        with pytest.raises(ValidationError):
            UserUpdate(email="invalid-email")
    
    def test_user_update_does_not_accept_password(self):
        """Test that password field was removed from UserUpdate (use PasswordChange instead)"""
        # Password can be passed but will be ignored since it's not a field in UserUpdate
        user_update = UserUpdate(
            email="test@example.com",
            name="Test User",
            password="somepassword123"  # This should be ignored
        )
        # UserUpdate should not have a password attribute
        assert not hasattr(user_update, 'password')
        # Only the valid fields should be set
        assert user_update.email == "test@example.com"
        assert user_update.name == "Test User"
    
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


class TestPasswordChangeModel:
    """Test suite for PasswordChange model"""
    
    # Valid creation tests
    
    def test_password_change_with_valid_data(self):
        """Test PasswordChange creation with valid data"""
        password_change = PasswordChange(
            current_password="oldpass123",
            new_password="newpass123"
        )
        assert password_change.current_password == "oldpass123"
        assert password_change.new_password == "newpass123"
    
    def test_password_change_with_minimum_length(self):
        """Test PasswordChange with minimum password length (8 characters)"""
        password_change = PasswordChange(
            current_password="12345678",
            new_password="abcdefgh"
        )
        assert password_change.current_password == "12345678"
        assert password_change.new_password == "abcdefgh"
    
    def test_password_change_with_long_passwords(self):
        """Test PasswordChange with long passwords"""
        long_password = "a" * 100
        password_change = PasswordChange(
            current_password=long_password,
            new_password=long_password + "new"
        )
        assert len(password_change.current_password) == 100
        assert len(password_change.new_password) == 103
    
    def test_password_change_with_special_characters(self):
        """Test PasswordChange with special characters in passwords"""
        password_change = PasswordChange(
            current_password="P@ssw0rd!#$%",
            new_password="N3w!P@ss#2024"
        )
        assert password_change.current_password == "P@ssw0rd!#$%"
        assert password_change.new_password == "N3w!P@ss#2024"
    
    def test_password_change_with_unicode_characters(self):
        """Test PasswordChange with unicode characters"""
        password_change = PasswordChange(
            current_password="pássw0rd123",
            new_password="新password123"
        )
        assert password_change.current_password == "pássw0rd123"
        assert password_change.new_password == "新password123"
    
    # Validation tests
    
    def test_password_change_without_current_password_fails(self):
        """Test PasswordChange creation fails without current_password"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(new_password="newpass123")
        errors = exc_info.value.errors()
        assert any("current_password" in str(error["loc"]) for error in errors)
    
    def test_password_change_without_new_password_fails(self):
        """Test PasswordChange creation fails without new_password"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(current_password="oldpass123")
        errors = exc_info.value.errors()
        assert any("new_password" in str(error["loc"]) for error in errors)
    
    def test_password_change_with_current_password_too_short(self):
        """Test PasswordChange fails with current_password shorter than 8 characters"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(current_password="short", new_password="validpass123")
        errors = exc_info.value.errors()
        assert any("current_password" in str(error["loc"]) for error in errors)
    
    def test_password_change_with_new_password_too_short(self):
        """Test PasswordChange fails with new_password shorter than 8 characters"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(current_password="validpass123", new_password="short")
        errors = exc_info.value.errors()
        assert any("new_password" in str(error["loc"]) for error in errors)
    
    def test_password_change_with_both_passwords_too_short(self):
        """Test PasswordChange fails when both passwords are too short"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(current_password="short", new_password="brief")
        errors = exc_info.value.errors()
        # Should have errors for both fields
        error_fields = [str(error["loc"]) for error in errors]
        assert any("current_password" in field for field in error_fields)
        assert any("new_password" in field for field in error_fields)
    
    def test_password_change_with_empty_current_password(self):
        """Test PasswordChange fails with empty current_password"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(current_password="", new_password="validpass123")
        errors = exc_info.value.errors()
        assert any("current_password" in str(error["loc"]) for error in errors)
    
    def test_password_change_with_empty_new_password(self):
        """Test PasswordChange fails with empty new_password"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(current_password="validpass123", new_password="")
        errors = exc_info.value.errors()
        assert any("new_password" in str(error["loc"]) for error in errors)
    
    def test_password_change_same_passwords_allowed(self):
        """Test PasswordChange allows same password for current and new (backend validates this)"""
        # Model validation doesn't prevent same passwords - business logic does
        password_change = PasswordChange(
            current_password="samepass123",
            new_password="samepass123"
        )
        assert password_change.current_password == password_change.new_password
    
    def test_password_change_model_dump(self):
        """Test PasswordChange model_dump serialization"""
        password_change = PasswordChange(
            current_password="oldpass123",
            new_password="newpass123"
        )
        dumped = password_change.model_dump()
        assert dumped["current_password"] == "oldpass123"
        assert dumped["new_password"] == "newpass123"
        assert len(dumped) == 2  # Only these two fields
    
    def test_password_change_model_dump_json(self):
        """Test PasswordChange model_dump_json serialization"""
        password_change = PasswordChange(
            current_password="oldpass123",
            new_password="newpass123"
        )
        json_str = password_change.model_dump_json()
        assert "oldpass123" in json_str
        assert "newpass123" in json_str


class TestCompleteUserModel:
    """Test suite for User model (complete database representation returned from DB)"""
    
    # Valid creation tests
    
    def test_user_with_required_fields_only(self):
        """Test User creation with only required fields (email, id, created_at)"""
        test_id = generate_uuid()
        test_datetime = datetime.now()
        user = User(
            id=test_id,
            email="test@example.com",
            created_at=test_datetime
        )
        assert user.email == "test@example.com"
        assert user.name is None
        assert user.id == test_id
        assert user.passwordHash is None
        assert user.role == UserRole.USER
        assert user.created_at == test_datetime
        assert user.email_verified is False
    
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
            contact_person_country_code="34",
            contact_person_phone_number="600000000",
            diversity_type="visual",
            role=UserRole.ADMIN,
            created_at=test_datetime,
            email_verified=True
        )
        assert user.id == test_id
        assert user.email == "complete@example.com"
        assert user.name == "Complete User"
        assert user.passwordHash == "$2b$12$hashed_password"
        assert user.contact_person_country_code == "34"
        assert user.contact_person_phone_number == "600000000"
        assert user.role == UserRole.ADMIN
        assert user.created_at == test_datetime
        assert user.email_verified is True
    
    # Default values tests
    
    def test_user_accepts_different_ids(self):
        """Test User accepts different UUIDs (from database)"""
        id1 = generate_uuid()
        id2 = generate_uuid()
        test_datetime = datetime.now()
        user1 = User(id=id1, email="user1@example.com", created_at=test_datetime)
        user2 = User(id=id2, email="user2@example.com", created_at=test_datetime)
        assert user1.id != user2.id
        assert user1.id == id1
        assert user2.id == id2
        assert isinstance(user1.id, UUID)
        assert isinstance(user2.id, UUID)
    
    def test_user_default_role_is_user(self):
        """Test User default role is USER"""
        user = User(id=generate_uuid(), email="test@example.com", created_at=datetime.now())
        assert user.role == UserRole.USER
    
    def test_user_default_email_verified_is_false(self):
        """Test User default email_verified is False"""
        user = User(id=generate_uuid(), email="test@example.com", created_at=datetime.now())
        assert user.email_verified is False
    
    def test_user_created_at_from_database(self):
        """Test User accepts created_at from database"""
        test_datetime = datetime(2024, 1, 15, 10, 30, 0)
        user = User(id=generate_uuid(), email="test@example.com", created_at=test_datetime)
        assert user.created_at == test_datetime
        assert isinstance(user.created_at, datetime)
    
    def test_user_without_password_hash(self):
        """Test User can be created without passwordHash when needed in memory"""
        user = User(
            id=generate_uuid(),
            email="nopassword@example.com",
            name="User Without Password",
            passwordHash=None,
            created_at=datetime.now()
        )
        assert user.passwordHash is None
        assert user.email == "nopassword@example.com"
    
    def test_user_for_traditional_auth_with_password_hash(self):
        """Test User with passwordHash for traditional authentication"""
        user = User(
            id=generate_uuid(),
            email="traditional@example.com",
            passwordHash="$2b$12$hashed_password",
            created_at=datetime.now()
        )
        assert user.passwordHash == "$2b$12$hashed_password"
    
    # Validation tests
    
    def test_user_without_email_fails(self):
        """Test User creation fails without email"""
        with pytest.raises(ValidationError) as exc_info:
            User(id=generate_uuid(), created_at=datetime.now())
        errors = exc_info.value.errors()
        assert any("email" in str(error["loc"]) for error in errors)
    
    def test_user_with_invalid_email_fails(self):
        """Test User creation fails with invalid email"""
        with pytest.raises(ValidationError):
            User(id=generate_uuid(), email="not-an-email", created_at=datetime.now())
    
    def test_user_with_invalid_role(self):
        """Test User creation fails with invalid role"""
        with pytest.raises(ValidationError):
            User(id=generate_uuid(), email="test@example.com", role="invalid_role", created_at=datetime.now())
    
    def test_user_with_wrong_type_email_verified(self):
        """Test User creation fails with wrong type for email_verified"""
        with pytest.raises(ValidationError):
            User(id=generate_uuid(), email="test@example.com", email_verified="not_a_boolean", created_at=datetime.now())


class TestUserInsertModel:
    """Test suite for UserInsert model (database insertion with split phone)"""
    
    # Valid creation tests
    
    def test_user_insert_with_required_fields(self):
        """Test UserInsert creation with only required fields"""
        test_id = generate_uuid()
        user_insert = UserInsert(
            id=test_id,
            email="insert@example.com",
            passwordHash="$2b$12$hashed_password"
        )
        assert user_insert.id == test_id
        assert user_insert.email == "insert@example.com"
        assert user_insert.passwordHash == "$2b$12$hashed_password"
        assert user_insert.name is None
        assert user_insert.contact_person_country_code is None
        assert user_insert.contact_person_phone_number is None
        assert user_insert.role == UserRole.USER
        assert user_insert.email_verified is False
        assert not hasattr(user_insert, 'created_at')  # Excluded from insert
    
    def test_user_insert_with_all_fields(self):
        """Test UserInsert creation with all fields including split phone"""
        test_id = generate_uuid()
        user_insert = UserInsert(
            id=test_id,
            email="complete@example.com",
            name="Complete User",
            passwordHash="$2b$12$hashed_password",
            contact_person_email="contact@example.com",
            contact_person_country_code="34",
            contact_person_phone_number="600123456",
            diversity_type="visual",
            role=UserRole.ADMIN,
            email_verified=True
        )
        assert user_insert.id == test_id
        assert user_insert.email == "complete@example.com"
        assert user_insert.name == "Complete User"
        assert user_insert.passwordHash == "$2b$12$hashed_password"
        assert user_insert.contact_person_country_code == "34"
        assert user_insert.contact_person_phone_number == "600123456"
        assert user_insert.diversity_type == "visual"
        assert user_insert.role == UserRole.ADMIN
        assert user_insert.email_verified is True
    
    def test_user_insert_split_phone_fields(self):
        """Test UserInsert with split phone country code and number"""
        user_insert = UserInsert(
            id=generate_uuid(),
            email="phone@example.com",
            passwordHash="$2b$12$hashed_password",
            contact_person_country_code="1",
            contact_person_phone_number="5551234567"
        )
        assert user_insert.contact_person_country_code == "1"
        assert user_insert.contact_person_phone_number == "5551234567"
        assert isinstance(user_insert.contact_person_country_code, str)
        assert isinstance(user_insert.contact_person_phone_number, str)
    
    # Default values tests
    
    def test_user_insert_default_role(self):
        """Test UserInsert default role is USER"""
        user_insert = UserInsert(
            id=generate_uuid(),
            email="test@example.com",
            passwordHash="$2b$12$hashed_password"
        )
        assert user_insert.role == UserRole.USER
    
    def test_user_insert_default_email_verified(self):
        """Test UserInsert default email_verified is False"""
        user_insert = UserInsert(
            id=generate_uuid(),
            email="test@example.com",
            passwordHash="$2b$12$hashed_password"
        )
        assert user_insert.email_verified is False
    
    # Validation tests
    
    def test_user_insert_auto_generates_id(self):
        """Test UserInsert auto-generates id if not provided"""
        user_insert1 = UserInsert(email="test1@example.com", passwordHash="$2b$12$hashed_password")
        user_insert2 = UserInsert(email="test2@example.com", passwordHash="$2b$12$hashed_password")
        assert user_insert1.id is not None
        assert user_insert2.id is not None
        assert user_insert1.id != user_insert2.id
        assert isinstance(user_insert1.id, UUID)
        assert isinstance(user_insert2.id, UUID)
    
    def test_user_insert_requires_email(self):
        """Test UserInsert fails without email"""
        with pytest.raises(ValidationError) as exc_info:
            UserInsert(id=generate_uuid())
        errors = exc_info.value.errors()
        assert any("email" in str(error["loc"]) for error in errors)
    
    def test_user_insert_with_invalid_email(self):
        """Test UserInsert fails with invalid email"""
        with pytest.raises(ValidationError):
            UserInsert(
                id=generate_uuid(),
                email="not-an-email",
                passwordHash="$2b$12$hashed_password"
            )
    
    def test_user_insert_with_invalid_role(self):
        """Test UserInsert fails with invalid role"""
        with pytest.raises(ValidationError):
            UserInsert(
                id=generate_uuid(),
                email="test@example.com",
                passwordHash="$2b$12$hashed_password",
                role="invalid_role"
            )
    
    def test_user_insert_country_code_as_string(self):
        """Test UserInsert accepts string country code"""
        user_insert = UserInsert(
            id=generate_uuid(),
            email="test@example.com",
            passwordHash="$2b$12$hashed_password",
            contact_person_country_code="44"
        )
        assert user_insert.contact_person_country_code == "44"
        assert isinstance(user_insert.contact_person_country_code, str)
    
    def test_user_insert_phone_number_as_string(self):
        """Test UserInsert accepts string phone number"""
        user_insert = UserInsert(
            id=generate_uuid(),
            email="test@example.com",
            passwordHash="$2b$12$hashed_password",
            contact_person_phone_number="7891234567"
        )
        assert user_insert.contact_person_phone_number == "7891234567"
        assert isinstance(user_insert.contact_person_phone_number, str)


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
            contact_person_country_code="34",
            contact_person_phone_number="600000000",
            diversity_type="visual",
            role=UserRole.USER,
            created_at=test_datetime,
            email_verified=True
        )
        assert user_response.id == test_id
        assert user_response.email == "response@example.com"
        assert user_response.name == "Response User"
        assert user_response.contact_person_country_code == "34"
        assert user_response.contact_person_phone_number == "600000000"
        assert user_response.role == UserRole.USER
        assert user_response.created_at == test_datetime
        assert user_response.email_verified is True
    
    def test_user_response_does_not_have_password_hash(self):
        """Test UserResponse does not expose passwordHash field"""
        test_id = generate_uuid()
        user_response = UserResponse(
            id=test_id,
            email="test@example.com",
            name="Test User",
            contact_person_email=None,
            contact_person_country_code=None,
            contact_person_phone_number=None,
            diversity_type=None,
            role=UserRole.USER,
            created_at=datetime.now(),
            email_verified=False
        )
        assert not hasattr(user_response, "passwordHash")
    
    def test_user_response_from_user_model(self):
        """Test creating UserResponse from User model (excluding sensitive data)"""
        user = User(
            id=generate_uuid(),
            email="user@example.com",
            name="Test User",
            passwordHash="$2b$12$sensitive_hash",
            created_at=datetime.now()
        )
        # Create response by excluding passwordHash
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            contact_person_email=user.contact_person_email,
            contact_person_country_code=user.contact_person_country_code,
            contact_person_phone_number=user.contact_person_phone_number,
            diversity_type=user.diversity_type,
            role=user.role,
            created_at=user.created_at,
            email_verified=user.email_verified
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
                email_verified=False
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
                email_verified=False
            )
        errors = exc_info.value.errors()
        assert any("email" in str(error["loc"]) for error in errors)
    
    def test_user_response_without_name(self):
        """Test UserResponse can be created without name (name is optional)"""
        user_response = UserResponse(
            id=generate_uuid(),
            email="test@example.com",
            role=UserRole.USER,
            created_at=datetime.now(),
            email_verified=False
        )
        assert user_response.email == "test@example.com"
        assert user_response.name is None
    
    def test_user_response_with_optional_fields_none(self):
        """Test UserResponse accepts None for optional fields"""
        user_response = UserResponse(
            id=generate_uuid(),
            email="test@example.com",
            name="Test User",
            contact_person_email=None,
            contact_person_country_code=None,
            contact_person_phone_number=None,
            diversity_type=None,
            role=UserRole.USER,
            created_at=datetime.now(),
            email_verified=False
        )
        assert user_response.contact_person_email is None
        assert user_response.contact_person_country_code is None
        assert user_response.contact_person_phone_number is None
        assert user_response.diversity_type is None
    


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
