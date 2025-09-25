from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth import AuthService
from app.schemas.user import UserCreate, LoginRequest, TokenResponse, RefreshTokenRequest

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя"""
    auth_service = AuthService(db)
    success, error = await auth_service.register_user(user_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
async def login(
        login_data: LoginRequest,
        db: AsyncSession = Depends(get_db)
):
    """Вход пользователя"""
    auth_service = AuthService(db)
    user_data, error = await auth_service.authenticate_user(login_data)

    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )

    tokens = await auth_service.create_tokens(user_data)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
        token_data: RefreshTokenRequest,
        db: AsyncSession = Depends(get_db)
):
    """Обновление токенов"""
    auth_service = AuthService(db)
    tokens, error = await auth_service.refresh_tokens(token_data.refresh_token)

    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )

    return tokens