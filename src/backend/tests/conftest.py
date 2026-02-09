"""
Global Test Configuration for TFG Application

This module provides shared fixtures and configuration for all tests.
"""

import pytest


@pytest.fixture(scope="function")
def sample_user_base_data() -> dict:
    """
    Provide sample UserBase data for testing.
    
    Returns:
        Dictionary with valid UserBase data
    """
    return {
        "email": "test@example.com",
        "name": "Test User",
        "contact_person_email": "contact@example.com",
        "contact_person_country_code": "34",
        "contact_person_phone_number": "600000000",
        "diversity_type": "visual",
    }

@pytest.fixture(scope="function")
def sample_user_create_data() -> dict:
    """
    Provide sample user creation data for testing.
    
    Returns:
        Dictionary with valid user creation data
    """
    return {
        "email": "test@example.com",
        "name": "Test User",
        "contact_person_email": "contact@example.com",
        "contact_person_country_code": "34",
        "contact_person_phone_number": "600000000",
        "diversity_type": "visual",
        "password": "testpassword123"
    }

@pytest.fixture(scope="function")
def sample_user_data() -> dict:
    """
    Provide sample user data for testing.
    
    Returns:
        Dictionary with valid user data
    """
    return {
        "email": "test@example.com",
        "name": "Test User",
        "contact_person_email": "contact@example.com",
        "contact_person_country_code": "34",
        "contact_person_phone_number": "600000000",
        "diversity_type": "visual",
    }


@pytest.fixture(scope="function")
def sample_user_update_data() -> dict:
    """
    Provide sample user update data for testing.
    
    Returns:
        Dictionary with valid user update data
    """
    return {
        "email": "updated@example.com",
        "name": "Updated User"
    }

