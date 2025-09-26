import pytest


class TestAuthAPI:
    def test_register_success(self, client):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "first_name": "New",
            "last_name": "User"
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        assert "message" in response.json()

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User"
        }

        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_login_success(self, client, test_user):
        """Test successful login."""
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    async def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "id" in data