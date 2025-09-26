from fastapi import APIRouter, Depends, HTTPException, status
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, LoginRequest, TokenResponse, RefreshTokenRequest
from app.api.dependencies import get_auth_service

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя"""
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
    auth_service: AuthService = Depends(get_auth_service)
):
    """Вход пользователя"""
    user_data, error = await auth_service.authenticate_user(login_data)

    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )

    tokens = await auth_service.create_tokens(user_data)

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tokens"
        )

    return tokens

@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    token_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Обновление токенов"""
    tokens, error = await auth_service.refresh_tokens(token_data.refresh_token)

    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )

    return tokens