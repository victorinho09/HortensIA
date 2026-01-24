# Testing

This directory contains all tests for the TFG application.

## Structure

```
tests/
├── conftest.py           # Global test configuration and fixtures
├── test_models.py        # Domain model tests
└── README.md            # This file
```

## Running Tests

### Install test dependencies

```bash
pip install pytest
```

### Run all tests

```bash
pytest
```





## Test Organization

- **conftest.py**: Shared fixtures and configuration
- **test_models.py**: Tests for domain models (User, UUID, etc.)

## Writing New Tests

1. Create test file: `test_<feature>.py`
2. Organize tests in classes: `class TestFeatureName`
3. Name test methods: `test_<what_it_tests>`
4. Use fixtures from conftest.py