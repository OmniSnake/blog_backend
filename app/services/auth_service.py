from typing import Optional, Tuple
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.core.security import SecurityService
from app.core.config import settings
from app.repositories.base import (
    UserRepositoryInterface,
    RefreshTokenRepositoryInterface,
    RoleRepositoryInterface
)
from app.schemas.user import LoginRequest, UserCreate
from app.models.user import User
from app.models.role import Role
from app.models.refresh_token import RefreshToken

logger = logging.getLogger(__name__)


class AuthService:
    """Сервис аутентификации (чистая бизнес-логика)"""

    def __init__(
            self,
            user_repository: UserRepositoryInterface[User],
            refresh_token_repository: RefreshTokenRepositoryInterface[RefreshToken],
            role_repository: RoleRepositoryInterface[Role],
            db_session: AsyncSession
    ):
        self._user_repository = user_repository
        self._refresh_token_repository = refresh_token_repository
        self._role_repository = role_repository
        self._db_session = db_session

    async def register_user(self, user_data: UserCreate) -> Tuple[bool, Optional[str]]:
        """Регистрация пользователя (бизнес-логика)"""
        try:
            if await self._user_repository.email_exists(user_data.email):
                return False, "User with this email already exists"

            password_hash = SecurityService.hash_password(user_data.password)

            user_dict = user_data.model_dump(exclude={'password'})
            user_dict['password_hash'] = password_hash

            user = await self._user_repository.create(**user_dict)
            if not user:
                return False, "Failed to create user"

            await self._db_session.commit()

            success = await self._assign_default_role(user.id)
            if not success:
                logger.warning(f"Failed to assign default role to user {user.id}, but user was created")

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during registration: {error}")
            return False, "Database error"
        except Exception as error:
            await self._db_session.rollback()
            logger.error(f"Unexpected error during registration: {error}")
            return False, "Registration failed"

    async def authenticate_user(self, login_data: LoginRequest) -> Tuple[Optional[dict], Optional[str]]:
        """Аутентификация пользователя (бизнес-логика)"""
        try:
            user = await self._user_repository.get_by_email(login_data.email)

            if not user or not user.is_active:
                return None, "Invalid credentials"

            if not SecurityService.verify_password(login_data.password, user.password_hash):
                return None, "Invalid credentials"

            user_with_roles = await self._user_repository.get_with_roles(user.id)
            roles = [role.name for role in user_with_roles.roles] if user_with_roles and user_with_roles.roles else []

            user_data = {
                "sub": str(user.id),
                "email": user.email,
                "roles": roles
            }

            return user_data, None

        except SQLAlchemyError as error:
            logger.error(f"Database error during authentication: {error}")
            return None, "Authentication error"
        except Exception as error:
            logger.error(f"Unexpected error during authentication: {error}")
            return None, "Authentication failed"

    async def create_tokens(self, user_data: dict) -> Optional[dict]:
        """Создание токенов (бизнес-логика)"""
        try:
            access_token = SecurityService.create_access_token(user_data)
            refresh_token = SecurityService.create_refresh_token(user_data)

            expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

            token_created = await self._refresh_token_repository.create(
                token=refresh_token,
                expires_at=expires_at,
                user_id=int(user_data["sub"])
            )

            if token_created:
                await self._db_session.commit()
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer"
                }
            return None

        except Exception as error:
            logger.error(f"Error creating tokens: {error}")
            return None

    async def refresh_tokens(self, refresh_token: str) -> Tuple[Optional[dict], Optional[str]]:
        """Обновление токенов (бизнес-логика)"""
        try:
            token_record = await self._refresh_token_repository.get_by_token(refresh_token)
            if not token_record or token_record.expires_at < datetime.now(UTC):
                return None, "Invalid or expired refresh token"

            payload = SecurityService.verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                return None, "Invalid token"

            user_id = int(payload["sub"])
            user = await self._user_repository.get_with_roles(user_id)
            if not user or not user.is_active:
                return None, "User not found"

            roles = [role.name for role in user.roles] if user.roles else []
            user_data = {
                "sub": str(user.id),
                "email": user.email,
                "roles": roles
            }

            tokens = await self.create_tokens(user_data)
            if not tokens:
                return None, "Failed to create tokens"

            await self._refresh_token_repository.delete(token_record.id)
            await self._db_session.commit()

            return tokens, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during token refresh: {error}")
            return None, "Database error"
        except Exception as error:
            logger.error(f"Unexpected error during token refresh: {error}")
            return None, "Token refresh failed"

    async def _assign_default_role(self, user_id: int) -> bool:
        """Назначить роль по умолчанию (внутренняя бизнес-логика)"""
        try:
            user = await self._user_repository.get_with_roles(user_id)
            role = await self._role_repository.get_by_name("user")

            if not user or not role:
                return False

            if role not in user.roles:
                user.roles.append(role)
                self._db_session.add(user)
                return True

            return False
        except SQLAlchemyError as error:
            logger.error(f"Error assigning default role to user {user_id}: {error}")
            return False