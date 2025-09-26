import pytest
from httpx import AsyncClient


class TestAuthAPI:
    @pytest.mark.asyncio
    async def test_register_success(self, client):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "first_name": "New",
            "last_name": "User"
        }

        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        assert "message" in response.json()

    async def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }

        response = await client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_login_success(self, client, test_user):
        """Test successful login."""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }

        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    async def test_refresh_tokens(self, client, test_user):
        """Test token refresh."""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()

        refresh_data = {
            "refresh_token": tokens["refresh_token"]
        }
        refresh_response = await client.post("/api/v1/auth/refresh", json=refresh_data)
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens