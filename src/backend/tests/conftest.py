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


@pytest.fixture(scope="function")
def sample_login_request_data() -> dict:
    """
    Provide sample LoginRequest data for testing.
    
    Returns:
        Dictionary with valid login request data
    """
    return {
        "email": "test@example.com",
        "password": "password123"
    }


@pytest.fixture(scope="function")
def sample_user_response_data() -> dict:
    """
    Provide sample UserResponse data for testing.
    
    Returns:
        Dictionary with valid UserResponse data
    """
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "test@example.com",
        "name": "Test User",
        "contact_person_email": "contact@example.com",
        "contact_person_country_code": "34",
        "contact_person_phone_number": "600000000",
        "diversity_type": "visual",
        "passwordHash": None,
        "role": "user",
        "email_verified": False,
        "settings": {},
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture(scope="function")
def sample_login_response_data(sample_user_response_data) -> dict:
    """
    Provide sample LoginResponse data for testing.
    
    Returns:
        Dictionary with valid login response data
    """
    return {
        "session_id": "123e4567-e89b-12d3-a456-426614174000",
        "user": sample_user_response_data
    }


@pytest.fixture(scope="function")
def sample_frame_message_data() -> dict:
    """Provide sample FrameMessage data for testing."""
    return {
        "type": "frame",
        "data": "aGVsbG8gd29ybGQ=",  # base64 of "hello world"
        "timestamp": 1709827200000.0,
    }


@pytest.fixture(scope="function")
def sample_detected_object_data() -> dict:
    """Provide sample DetectedObject data for testing."""
    return {
        "class_name": "car",
        "confidence": 0.92,
        "bbox": [0.1, 0.2, 0.5, 0.8],
        "zone": "bottom",
        "supercategory": "vehicle",
        "supercategory_risk_level": "low",
        "supercategory_risk_weight": 0.25,
        "effective_risk_level": "low",
        "effective_risk_weight": 0.25,
        "risk_source": "supercategory_base",
    }


@pytest.fixture(scope="function")
def sample_alert_message_data() -> dict:
    """Provide sample AlertMessage data for testing."""
    return {
        "message": "Caution, car detected nearby",
        "severity": "critical",
        "objects": [
            {
                "class_name": "car",
                "confidence": 0.92,
                "bbox": [0.1, 0.2, 0.5, 0.8],
                "zone": "bottom",
                "supercategory": "vehicle",
                "supercategory_risk_level": "low",
                "supercategory_risk_weight": 0.25,
                "effective_risk_level": "low",
                "effective_risk_weight": 0.25,
                "risk_source": "supercategory_base",
            }
        ],
        "timestamp": 1709827200000.0,
    }
