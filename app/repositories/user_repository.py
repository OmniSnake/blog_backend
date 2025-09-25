from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.user import User
from app.repositories.base import UserRepositoryInterface

logger = logging.getLogger(__name__)


class UserRepository(UserRepositoryInterface[User]):
    """Конкретная реализация репозитория пользователей (только данные)"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self._model = User

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        try:
            result = await self._db_session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Error getting user by id {user_id}: {error}")
            return None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        try:
            result = await self._db_session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Error getting user by email {email}: {error}")
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить всех пользователей"""
        try:
            result = await self._db_session.execute(
                select(User).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except SQLAlchemyError as error:
            logger.error(f"Error getting all users: {error}")
            return []

    async def get_with_roles(self, user_id: int) -> Optional[User]:
        """Получить пользователя с ролями"""
        try:
            from sqlalchemy.orm import selectinload

            result = await self._db_session.execute(
                select(User)
                .options(selectinload(User.roles))
                .where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if user and hasattr(user, 'roles'):
                _ = user.roles

            return user
        except SQLAlchemyError as error:
            logger.error(f"Error getting user with roles {user_id}: {error}")
            return None

    async def email_exists(self, email: str) -> bool:
        """Проверить существование email"""
        try:
            result = await self._db_session.execute(
                select(User.id).where(User.email == email)
            )
            return result.scalar() is not None
        except SQLAlchemyError as error:
            logger.error(f"Error checking email existence {email}: {error}")
            return False

    async def create(self, **kwargs) -> Optional[User]:
        """Создать пользователя"""
        try:
            user = User(**kwargs)
            self._db_session.add(user)
            return user
        except SQLAlchemyError as error:
            logger.error(f"Error creating user: {error}")
            return None

    async def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Обновить пользователя"""
        try:
            user = await self.get_by_id(user_id)
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
            return user
        except SQLAlchemyError as error:
            logger.error(f"Error updating user {user_id}: {error}")
            return None

    async def delete(self, user_id: int) -> bool:
        """Удалить пользователя (soft delete)"""
        try:
            user = await self.get_by_id(user_id)
            if user:
                user.is_active = False
                return True
            return False
        except SQLAlchemyError as error:
            logger.error(f"Error deleting user {user_id}: {error}")
            return False