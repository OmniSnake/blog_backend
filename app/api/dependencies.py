from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.security import SecurityService
from app.core.database import get_db
from app.repositories.user import UserRepository
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
) -> dict:
    """Зависимость для получения текущего пользователя с оптимизацией запросов"""
    token = credentials.credentials
    payload = SecurityService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(
        int(payload["sub"]),
        options=[selectinload(User.roles)]
    )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    roles = [role.name for role in user.roles]

    return {
        "id": user.id,
        "email": user.email,
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