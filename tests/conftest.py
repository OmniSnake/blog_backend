import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import db_manager, get_db
from app.main import app
from app.models.base import Base
from app.core.security import SecurityService

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine):
    """Create a fresh database session for each test."""
    async with engine.connect() as connection:
        await connection.begin()

        async_session = async_sessionmaker(
            connection, expire_on_commit=False, class_=AsyncSession
        )

        async with async_session() as session:
            yield session

        await connection.rollback()


@pytest_asyncio.fixture
async def client(session):
    """Create test client with overridden database dependency."""

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(session):
    """Create a test user."""
    from app.models.user import User
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(session)
    user_data = {
        "email": "test@example.com",
        "password_hash": SecurityService.hash_password("testpassword123"),
        "first_name": "Test",
        "last_name": "User",
        "is_verified": True
    }

    user = await user_repo.create(**user_data)
    await session.commit()
    return user


@pytest_asyncio.fixture
async def test_admin_user(session):
    """Create a test admin user."""
    from app.models.user import User
    from app.models.role import Role
    from app.repositories.user_repository import UserRepository
    from app.repositories.role_repository import RoleRepository

    user_repo = UserRepository(session)
    role_repo = RoleRepository(session)

    admin_role = await role_repo.get_by_name("admin")
    if not admin_role:
        admin_role = await role_repo.create(
            name="admin",
            description="Administrator",
            permissions="all"
        )

    user_data = {
        "email": "admin@example.com",
        "password_hash": SecurityService.hash_password("adminpassword123"),
        "first_name": "Admin",
        "last_name": "User",
        "is_verified": True
    }

    user = await user_repo.create(**user_data)
    user.roles = [admin_role]
    await session.commit()
    return user


@pytest_asyncio.fixture
async def test_category(session):
    """Create a test category."""
    from app.repositories.category_repository import CategoryRepository

    category_repo = CategoryRepository(session)
    category_data = {
        "name": "Test Category",
        "slug": "test-category",
        "description": "Test category description"
    }

    category = await category_repo.create(**category_data)
    await session.commit()
    return category


@pytest_asyncio.fixture
async def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }

    response = await client.post("/api/v1/auth/login", json=login_data)
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest_asyncio.fixture
async def admin_headers(client, test_admin_user):
    """Get authentication headers for admin user."""
    login_data = {
        "email": "admin@example.com",
        "password": "adminpassword123"
    }

    response = await client.post("/api/v1/auth/login", json=login_data)
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}