import pytest
import pytest_asyncio
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, LoginRequest


class TestAuthService:
    @pytest_asyncio.fixture
    async def auth_service(self, session):
        from app.repositories.user_repository import UserRepository
        from app.repositories.refresh_token_repository import RefreshTokenRepository
        from app.repositories.role_repository import RoleRepository

        user_repo = UserRepository(session)
        token_repo = RefreshTokenRepository(session)
        role_repo = RoleRepository(session)

        return AuthService(user_repo, token_repo, role_repo, session)

    async def test_register_user_success(self, auth_service):
        """Test successful user registration."""
        user_data = UserCreate(
            email="newuser@example.com",
            password="securepassword123",
            first_name="New",
            last_name="User"
        )

        success, error = await auth_service.register_user(user_data)
        assert success is True
        assert error is None

    async def test_register_user_duplicate_email(self, auth_service, test_user):
        """Test registration with duplicate email."""
        user_data = UserCreate(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        )

        success, error = await auth_service.register_user(user_data)
        assert success is False
        assert "already exists" in error

    async def test_authenticate_user_success(self, auth_service, test_user):
        """Test successful user authentication."""
        login_data = LoginRequest(
            email="test@example.com",
            password="testpassword123"
        )

        user_data, error = await auth_service.authenticate_user(login_data)
        assert user_data is not None
        assert error is None
        assert user_data["email"] == "test@example.com"

    async def test_authenticate_user_invalid_credentials(self, auth_service):
        """Test authentication with invalid credentials."""
        login_data = LoginRequest(
            email="nonexistent@example.com",
            password="wrongpassword"
        )

        user_data, error = await auth_service.authenticate_user(login_data)
        assert user_data is None
        assert error is not None

    async def test_create_tokens(self, auth_service, test_user):
        """Test token creation."""
        user_data = {
            "sub": str(test_user.id),
            "email": test_user.email,
            "roles": ["user"]
        }

        tokens = await auth_service.create_tokens(user_data)
        assert tokens is not None
        assert "access_token" in tokens
        assert "refresh_token" in tokens