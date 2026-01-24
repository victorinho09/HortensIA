"""
Hash Module Tests

Unit tests for password hashing and verification functions.
"""

import pytest
from backend.models.hash import hash_password, verify_password, needs_rehash


class TestHashPassword:
    """Test suite for hash_password function"""
    
    # Valid hashing tests
    
    def test_hash_password_returns_string(self):
        """Test hash_password returns a string"""
        hashed = hash_password("myPassword123")
        assert isinstance(hashed, str)
    
    def test_hash_password_returns_argon2_format(self):
        """Test hash_password returns Argon2 formatted hash"""
        hashed = hash_password("myPassword123")
        assert hashed.startswith("$argon2")
    
    def test_hash_password_creates_unique_hashes(self):
        """Test same password creates different hashes (due to salt)"""
        password = "samePassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2
    
    def test_hash_password_with_min_length_password(self):
        """Test hash_password works with short passwords"""
        hashed = hash_password("a")
        assert isinstance(hashed, str)
        assert hashed.startswith("$argon2")
    
    def test_hash_password_with_long_password(self):
        """Test hash_password works with long passwords"""
        long_password = "a" * 1000
        hashed = hash_password(long_password)
        assert isinstance(hashed, str)
        assert hashed.startswith("$argon2")
    
    def test_hash_password_with_special_characters(self):
        """Test hash_password works with special characters"""
        password = "p@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert hashed.startswith("$argon2")
    
    def test_hash_password_with_unicode_characters(self):
        """Test hash_password works with unicode characters"""
        password = "contraseña_中文_🔒"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert hashed.startswith("$argon2")
    
    # Error handling tests
    
    def test_hash_password_with_empty_string_fails(self):
        """Test hash_password fails with empty string"""
        with pytest.raises(ValueError) as exc_info:
            hash_password("")
        assert "empty" in str(exc_info.value).lower()
    
    def test_hash_password_with_non_string_fails(self):
        """Test hash_password fails with non-string input"""
        with pytest.raises(TypeError) as exc_info:
            hash_password(12345)
        assert "string" in str(exc_info.value).lower()
    
    def test_hash_password_with_none_fails(self):
        """Test hash_password fails with None"""
        with pytest.raises(TypeError):
            hash_password(None)
    
    def test_hash_password_with_list_fails(self):
        """Test hash_password fails with list"""
        with pytest.raises(TypeError):
            hash_password(["password"])
    
    def test_hash_password_with_dict_fails(self):
        """Test hash_password fails with dict"""
        with pytest.raises(TypeError):
            hash_password({"password": "test"})


class TestVerifyPassword:
    """Test suite for verify_password function"""
    
    # Valid verification tests
    
    def test_verify_password_with_correct_password(self):
        """Test verify_password returns True for correct password"""
        password = "correctPassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_with_incorrect_password(self):
        """Test verify_password returns False for incorrect password"""
        password = "correctPassword123"
        hashed = hash_password(password)
        assert verify_password("wrongPassword", hashed) is False
    
    def test_verify_password_case_sensitive(self):
        """Test verify_password is case sensitive"""
        password = "CaseSensitive"
        hashed = hash_password(password)
        assert verify_password("casesensitive", hashed) is False
        assert verify_password("CASESENSITIVE", hashed) is False
    
    def test_verify_password_with_special_characters(self):
        """Test verify_password works with special characters"""
        password = "p@ssw0rd!#$%"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("p@ssw0rd!#$", hashed) is False
    
    def test_verify_password_with_unicode(self):
        """Test verify_password works with unicode characters"""
        password = "contraseña_中文_🔒"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_with_empty_password(self):
        """Test verify_password handles empty password correctly"""
        password = "actualPassword"
        hashed = hash_password(password)
        assert verify_password("", hashed) is False
    
    def test_verify_password_with_whitespace_differences(self):
        """Test verify_password detects whitespace differences"""
        password = "password"
        hashed = hash_password(password)
        assert verify_password("password ", hashed) is False
        assert verify_password(" password", hashed) is False
    
    # Error handling tests
    
    def test_verify_password_with_invalid_hash_format(self):
        """Test verify_password returns False for invalid hash format"""
        password = "password123"
        invalid_hash = "not_a_valid_hash"
        assert verify_password(password, invalid_hash) is False
    
    def test_verify_password_with_empty_hash(self):
        """Test verify_password returns False for empty hash"""
        assert verify_password("password", "") is False
    
    def test_verify_password_with_wrong_hash_algorithm(self):
        """Test verify_password returns False for different hash algorithm"""
        # BCrypt hash instead of Argon2
        bcrypt_hash = "$2b$12$abcdefghijklmnopqrstuv"
        assert verify_password("password", bcrypt_hash) is False
    
    def test_verify_password_with_truncated_hash(self):
        """Test verify_password returns False for truncated hash"""
        password = "password123"
        hashed = hash_password(password)
        truncated = hashed[:20]
        assert verify_password(password, truncated) is False
    
    # Multiple password verification tests
    
    def test_verify_password_multiple_passwords(self):
        """Test verify_password works correctly for multiple passwords"""
        passwords = ["pass1", "pass2", "pass3"]
        hashes = [hash_password(p) for p in passwords]
        
        # Verify each password matches its own hash
        for i, password in enumerate(passwords):
            assert verify_password(password, hashes[i]) is True
        
        # Verify passwords don't match other hashes
        assert verify_password(passwords[0], hashes[1]) is False
        assert verify_password(passwords[1], hashes[2]) is False
        assert verify_password(passwords[2], hashes[0]) is False


class TestNeedsRehash:
    """Test suite for needs_rehash function"""
    
    # Valid rehash checking tests
    
    def test_needs_rehash_with_current_hash(self):
        """Test needs_rehash returns False for freshly created hash"""
        password = "testPassword123"
        hashed = hash_password(password)
        assert needs_rehash(hashed) is False
    
    def test_needs_rehash_with_valid_hash_format(self):
        """Test needs_rehash works with valid Argon2 hash"""
        hashed = hash_password("password")
        result = needs_rehash(hashed)
        assert isinstance(result, bool)
    
    # Error handling tests
    
    def test_needs_rehash_with_invalid_hash(self):
        """Test needs_rehash returns True for invalid hash"""
        invalid_hash = "not_a_valid_hash"
        assert needs_rehash(invalid_hash) is True
    
    def test_needs_rehash_with_empty_string(self):
        """Test needs_rehash returns True for empty string"""
        assert needs_rehash("") is True
    
    def test_needs_rehash_with_wrong_algorithm_hash(self):
        """Test needs_rehash returns True for different algorithm"""
        bcrypt_hash = "$2b$12$abcdefghijklmnopqrstuv"
        assert needs_rehash(bcrypt_hash) is True
    
    def test_needs_rehash_with_truncated_hash(self):
        """Test needs_rehash returns True for truncated hash"""
        hashed = hash_password("password")
        truncated = hashed[:20]
        assert needs_rehash(truncated) is True


class TestHashingIntegration:
    """Integration tests for the complete hashing workflow"""
    
    def test_complete_password_lifecycle(self):
        """Test complete workflow: hash, verify, check rehash"""
        password = "mySecurePassword123!"
        
        # Hash the password
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        
        # Verify correct password
        assert verify_password(password, hashed) is True
        
        # Verify incorrect password
        assert verify_password("wrongPassword", hashed) is False
        
        # Check if rehash is needed (should be False for new hash)
        assert needs_rehash(hashed) is False
    
    def test_multiple_users_workflow(self):
        """Test hashing workflow for multiple users with same password"""
        password = "commonPassword123"
        
        # Create hashes for multiple users with same password
        user1_hash = hash_password(password)
        user2_hash = hash_password(password)
        user3_hash = hash_password(password)
        
        # Hashes should be different (unique salts)
        assert user1_hash != user2_hash
        assert user2_hash != user3_hash
        
        # All should verify correctly
        assert verify_password(password, user1_hash) is True
        assert verify_password(password, user2_hash) is True
        assert verify_password(password, user3_hash) is True
    
    def test_password_change_workflow(self):
        """Test workflow when user changes password"""
        old_password = "oldPassword123"
        new_password = "newPassword456"
        
        # Hash old password
        old_hash = hash_password(old_password)
        
        # Verify old password works
        assert verify_password(old_password, old_hash) is True
        
        # User changes password
        new_hash = hash_password(new_password)
        
        # Old password shouldn't work with new hash
        assert verify_password(old_password, new_hash) is False
        
        # New password should work with new hash
        assert verify_password(new_password, new_hash) is True
        
        # Old hash shouldn't work with new password
        assert verify_password(new_password, old_hash) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
