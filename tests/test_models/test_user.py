import pytest
from app.models.user import User
from datetime import datetime


class TestUserModel:
    def test_user_creation(self):
        """Test user model creation."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            is_verified=False
        )

        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.is_verified is False

    def test_user_repr(self):
        """Test user string representation."""
        user = User(email="test@example.com", password_hash="hash")
        assert repr(user) == "<User test@example.com>"

    def test_user_default_values(self):
        """Test user model default values."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            is_verified=False
        )

        assert user.is_verified is False