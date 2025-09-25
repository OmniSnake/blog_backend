from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.schemas.user import UserWithRolesResponse

router = APIRouter()


@router.get("/me", response_model=UserWithRolesResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Получить информацию о текущем пользователе"""
    return UserWithRolesResponse(
        id=current_user["id"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        is_verified=current_user["is_verified"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
        updated_at=current_user["updated_at"],
        roles=current_user["roles"]
    )