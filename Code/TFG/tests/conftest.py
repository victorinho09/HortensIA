"""
Global Test Configuration for TFG Application

This module provides shared fixtures and configuration for all tests.
"""

import pytest


@pytest.fixture(scope="function")
def sample_user_create_data() -> dict:
    """
    Provide sample user creation data for testing.
    
    Returns:
        Dictionary with valid user creation data
    """
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "contact_person_email": "contact@example.com",
        "contact_person_phone": "+34600000000",
        "functional_diversity_type": "visual",
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
        "full_name": "Test User",
        "contact_person_email": "contact@example.com",
        "contact_person_phone": "+34600000000",
        "functional_diversity_type": "visual",
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
        "full_name": "Updated User"
    }

