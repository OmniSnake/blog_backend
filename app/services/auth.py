from typing import Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.core.security import SecurityService
from app.repositories.user import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.role import RoleRepository
from app.schemas.user import LoginRequest, UserCreate
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Сервис аутентификации"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.user_repo = UserRepository(db_session)
        self.token_repo = RefreshTokenRepository(db_session)
        self.role_repo = RoleRepository(db_session)

    async def register_user(self, user_data: UserCreate) -> Tuple[bool, Optional[str]]:
        """Регистрация нового пользователя"""
        try:
            existing_user = await self.user_repo.get_by_email(user_data.email)
            if existing_user:
                return False, "User already exists"

            password_hash = SecurityService.hash_password(user_data.password)

            user_dict = user_data.model_dump(exclude={'password'})
            user_dict['password_hash'] = password_hash

            user = await self.user_repo.create(**user_dict)
            if not user:
                return False, "Failed to create user"

            await self.db_session.commit()

            # Добавляем роль пользователю
            success = await self.user_repo.add_role_to_user(user.id, "user")
            if success:
                await self.db_session.commit()
                return True, None
            else:
                logger.warning(f"Failed to add user role to user {user.id}, but user was created")
                return True, None

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Database error during registration: {e}")
            return False, "Database error"
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Unexpected error during registration: {e}")
            return False, "Registration failed"

    async def authenticate_user(self, login_data: LoginRequest) -> Tuple[Optional[dict], Optional[str]]:
        """Аутентификация пользователя"""
        try:
            user = await self.user_repo.get_by_email(login_data.email)
            if not user or not user.is_active:
                return None, "Invalid credentials"

            if not SecurityService.verify_password(login_data.password, user.password_hash):
                return None, "Invalid credentials"

            roles = await self.user_repo.get_user_roles(user.id)

            user_data = {
                "sub": str(user.id),
                "email": user.email,
                "roles": roles
            }

            return user_data, None

        except SQLAlchemyError as e:
            logger.error(f"Database error during authentication: {e}")
            return None, "Authentication error"
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            return None, "Authentication failed"

    async def create_tokens(self, user_data: dict) -> Optional[dict]:
        """Создание access и refresh токенов"""
        try:
            access_token = SecurityService.create_access_token(user_data)
            refresh_token = SecurityService.create_refresh_token(user_data)

            expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            token_created = await self.token_repo.create(
                token=refresh_token,
                expires_at=expires_at,
                user_id=int(user_data["sub"])
            )

            if token_created:
                await self.db_session.commit()
            else:
                return None

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
        except Exception as e:
            logger.error(f"Error creating tokens: {e}")
            return None

    async def refresh_tokens(self, refresh_token: str) -> Tuple[Optional[dict], Optional[str]]:
        """Обновление токенов"""
        try:
            token_record = await self.token_repo.get_by_token(refresh_token)
            if not token_record or token_record.expires_at < datetime.utcnow():
                return None, "Invalid or expired refresh token"

            payload = SecurityService.verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                return None, "Invalid token"

            user_id = int(payload["sub"])
            user = await self.user_repo.get_by_id(user_id)
            if not user or not user.is_active:
                return None, "User not found"

            roles = await self.user_repo.get_user_roles(user.id)
            user_data = {
                "sub": str(user.id),
                "email": user.email,
                "roles": roles
            }

            tokens = await self.create_tokens(user_data)
            if not tokens:
                return None, "Failed to create tokens"

            await self.db_session.delete(token_record)
            await self.db_session.commit()

            return tokens, None

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Database error during token refresh: {e}")
            return None, "Database error"
        except Exception as e:
            logger.error(f"Unexpected error during token refresh: {e}")
            return None, "Token refresh failed"