from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import require_admin
from app.schemas.user import UserWithRolesResponse, UserRoleUpdate, UserListResponse
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository

router = APIRouter()


@router.get("/", response_model=UserListResponse)
async def get_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        current_user: dict = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Получение списка пользователей (только для администраторов)"""
    user_repo = UserRepository(db)
    users = await user_repo.get_all(skip=skip, limit=limit)

    users_with_roles = []
    for user in users:
        roles = await user_repo.get_user_roles(user.id)
        users_with_roles.append(
            UserWithRolesResponse(
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
        )

    return UserListResponse(
        users=users_with_roles,
        total=len(users_with_roles),
        skip=skip,
        limit=limit
    )


@router.put("/{user_id}/roles", response_model=UserWithRolesResponse)
async def update_user_roles(
        user_id: int,
        roles_data: UserRoleUpdate,
        current_user: dict = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Обновление ролей пользователя (только для администраторов)"""
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)

    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    current_roles = await user_repo.get_user_roles(user_id)

    for role_name in current_roles:
        pass

    for role_name in roles_data.roles:
        role = await role_repo.get_by_name(role_name)
        if role:
            await user_repo.add_role_to_user(user_id, role_name)

    await db.commit()

    updated_roles = await user_repo.get_user_roles(user_id)

    return UserWithRolesResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_verified=user.is_verified,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=updated_roles
    )