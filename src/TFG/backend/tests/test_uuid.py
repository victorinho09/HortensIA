"""
UUID Module Tests

Unit tests for UUID generation and validation utilities.
"""

import pytest
from uuid import UUID
from backend.models import UUIDType, generate_uuid, validate_uuid


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
