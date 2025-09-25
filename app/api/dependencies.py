from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import SecurityService
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.post_repository import PostRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.services.category_service import CategoryService
from app.services.post_service import PostService

security = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
) -> dict:
    """Зависимость для получения текущего пользователя"""
    token = credentials.credentials
    payload = SecurityService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user_repository = UserRepository(db)
    user = await user_repository.get_with_roles(int(payload["sub"]))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    roles = [role.name for role in user.roles] if user.roles else []

    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_verified": user.is_verified,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "roles": roles
    }


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Зависимость для проверки прав администратора"""
    if "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user


async def require_authenticated(current_user: dict = Depends(get_current_user)) -> dict:
    """Зависимость для проверки аутентификации (любой авторизованный пользователь)"""
    return current_user


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Фабрика для создания репозитория пользователей"""
    return UserRepository(db)


async def get_role_repository(db: AsyncSession = Depends(get_db)) -> RoleRepository:
    """Фабрика для создания репозитория ролей"""
    return RoleRepository(db)


async def get_category_repository(db: AsyncSession = Depends(get_db)) -> CategoryRepository:
    """Фабрика для создания репозитория категорий"""
    return CategoryRepository(db)


async def get_post_repository(db: AsyncSession = Depends(get_db)) -> PostRepository:
    """Фабрика для создания репозитория постов"""
    return PostRepository(db)


async def get_refresh_token_repository(db: AsyncSession = Depends(get_db)) -> RefreshTokenRepository:
    """Фабрика для создания репозитория refresh токенов"""
    return RefreshTokenRepository(db)


async def get_auth_service(
        user_repo: UserRepository = Depends(get_user_repository),
        token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
        role_repo: RoleRepository = Depends(get_role_repository),
        db: AsyncSession = Depends(get_db)
) -> AuthService:
    """Фабрика для создания сервиса аутентификации"""
    return AuthService(user_repo, token_repo, role_repo, db)


async def get_user_service(
        user_repo: UserRepository = Depends(get_user_repository),
        role_repo: RoleRepository = Depends(get_role_repository),
        db: AsyncSession = Depends(get_db)
) -> UserService:
    """Фабрика для создания сервиса пользователей"""
    return UserService(user_repo, role_repo, db)


async def get_role_service(
        user_repo: UserRepository = Depends(get_user_repository),
        role_repo: RoleRepository = Depends(get_role_repository),
        db: AsyncSession = Depends(get_db)
) -> RoleService:
    """Фабрика для создания сервиса ролей"""
    return RoleService(user_repo, role_repo, db)


async def get_category_service(
        category_repo: CategoryRepository = Depends(get_category_repository),
        post_repo: PostRepository = Depends(get_post_repository),
        db: AsyncSession = Depends(get_db)
) -> CategoryService:
    """Фабрика для создания сервиса категорий"""
    return CategoryService(category_repo, post_repo, db)


async def get_post_service(
        post_repo: PostRepository = Depends(get_post_repository),
        category_repo: CategoryRepository = Depends(get_category_repository),
        db: AsyncSession = Depends(get_db)
) -> PostService:
    """Фабрика для создания сервиса постов"""
    return PostService(post_repo, category_repo, db)
