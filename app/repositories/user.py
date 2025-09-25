from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.user import User
from app.models.role import Role
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """Репозиторий для пользователей"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        try:
            result = await self.db_session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    async def add_role_to_user(self, user_id: int, role_name: str) -> bool:
        """Добавить роль пользователю"""
        try:
            from sqlalchemy.orm import selectinload

            user_result = await self.db_session.execute(
                select(User).where(User.id == user_id).options(selectinload(User.roles))
            )
            user = user_result.scalar_one_or_none()

            role_result = await self.db_session.execute(
                select(Role).where(Role.name == role_name)
            )
            role = role_result.scalar_one_or_none()

            if user and role:
                if role not in user.roles:
                    user.roles.append(role)
                    self.db_session.add(user)
                    return True

            return False

        except SQLAlchemyError as e:
            logger.error(f"Error adding role {role_name} to user {user_id}: {e}")
            return False

    async def get_user_roles(self, user_id: int) -> List[str]:
        """Получить роли пользователя"""
        try:
            from sqlalchemy.orm import selectinload

            result = await self.db_session.execute(
                select(User).where(User.id == user_id).options(selectinload(User.roles))
            )
            user = result.scalar_one_or_none()

            if not user:
                return []
            return [role.name for role in user.roles]
        except SQLAlchemyError as e:
            logger.error(f"Error getting roles for user {user_id}: {e}")
            return []