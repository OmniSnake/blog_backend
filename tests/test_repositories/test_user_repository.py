import pytest
import pytest_asyncio
from app.repositories.user_repository import UserRepository


class TestUserRepository:
    @pytest_asyncio.fixture
    async def user_repo(self, session):
        return UserRepository(session)

    @pytest_asyncio.fixture
    async def test_user_data(self, user_repo, session):
        user_data = {
            "email": "repo_test@example.com",
            "password_hash": "hashed_password",
            "first_name": "Repo",
            "last_name": "Test"
        }
        user = await user_repo.create(**user_data)
        await session.commit()
        return user

    async def test_create_user(self, user_repo, session):
        """Test creating a user."""
        user_data = {
            "email": "new@example.com",
            "password_hash": "hash",
            "first_name": "New",
            "last_name": "User"
        }

        user = await user_repo.create(**user_data)
        await session.commit()

        assert user is not None
        assert user.email == "new@example.com"
        assert user.id is not None

    async def test_get_by_id(self, user_repo, test_user_data):
        """Test getting user by ID."""
        user = await user_repo.get_by_id(test_user_data.id)
        assert user is not None
        assert user.email == test_user_data.email

    async def test_get_by_email(self, user_repo, test_user_data):
        """Test getting user by email."""
        user = await user_repo.get_by_email("repo_test@example.com")
        assert user is not None
        assert user.id == test_user_data.id

    async def test_email_exists(self, user_repo, test_user_data):
        """Test email existence check."""
        exists = await user_repo.email_exists("repo_test@example.com")
        assert exists is True

        exists = await user_repo.email_exists("nonexistent@example.com")
        assert exists is False

    async def test_update_user(self, user_repo, test_user_data, session):
        """Test updating a user."""
        updated = await user_repo.update(
            test_user_data.id,
            first_name="Updated",
            last_name="Name"
        )
        await session.commit()

        assert updated.first_name == "Updated"
        assert updated.last_name == "Name"

    async def test_delete_user(self, user_repo, test_user_data, session):
        """Test soft deleting a user."""
        success = await user_repo.delete(test_user_data.id)
        await session.commit()

        assert success is True

        user = await user_repo.get_by_id(test_user_data.id)
        assert user.is_active is False