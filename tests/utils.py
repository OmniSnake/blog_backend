import json
from typing import Dict, Any


def assert_dict_contains(subset: Dict[str, Any], fullset: Dict[str, Any]):
    """Assert that fullset contains all key-value pairs from subset."""
    for key, value in subset.items():
        assert key in fullset, f"Key '{key}' not found in dictionary"
        assert fullset[key] == value, f"Value for key '{key}' does not match: {fullset[key]} != {value}"


async def create_test_user(client, user_data=None):
    """Helper to create a test user."""
    if user_data is None:
        user_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }

    response = await client.post("/api/v1/auth/register", json=user_data)
    return response


async def login_test_user(client, email, password):
    """Helper to login a test user."""
    login_data = {"email": email, "password": password}
    response = await client.post("/api/v1/auth/login", json=login_data)
    return response