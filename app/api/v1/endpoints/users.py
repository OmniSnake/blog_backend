from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.user import UserWithRolesResponse
from app.repositories.user import UserRepository

router = APIRouter()


@router.get("/me", response_model=UserWithRolesResponse)
async def get_current_user_info(
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """Получить информацию о текущем пользователе"""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user["id"])
    roles = await user_repo.get_user_roles(user.id)

    return UserWithRolesResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_verified=user.is_verified,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=roles
    )