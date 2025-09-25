from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(UserBase):
    """Схема ответа пользователя"""
    id: int
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True



class UserWithRolesResponse(UserResponse):
    """Схема ответа пользователя с ролями"""
    roles: Optional[List[str]] = None


class LoginRequest(BaseModel):
    """Схема для входа"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Схема ответа токена"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Схема для обновления токена"""
    refresh_token: str