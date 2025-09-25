from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.api.dependencies import require_admin, get_user_service, get_user_repository
from app.schemas.user import UserWithRolesResponse, UserRoleUpdate, UserListResponse
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

router = APIRouter()


@router.get("/", response_model=UserListResponse)
async def get_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        current_user: dict = Depends(require_admin),
        user_service: UserService = Depends(get_user_service),
        user_repository: UserRepository = Depends(get_user_repository)
):
    """Получение списка пользователей (только для администраторов)"""
    users = await user_repository.get_all(skip=skip, limit=limit)

    users_with_roles = []
    for user in users:
        roles = await user_service.get_user_roles(user.id)
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
        user_service: UserService = Depends(get_user_service),
        user_repository: UserRepository = Depends(get_user_repository)
):
    """Обновление ролей пользователя (только для администраторов)"""
    success, error = await user_service.update_user_roles(user_id, roles_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    user = await user_repository.get_by_id(user_id)
    updated_roles = await user_service.get_user_roles(user_id)

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


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
        user_id: int,
        current_user: dict = Depends(require_admin),
        user_service: UserService = Depends(get_user_service)
):
    """Деактивация пользователя (только для администраторов)"""
    success, error = await user_service.deactivate_user(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )