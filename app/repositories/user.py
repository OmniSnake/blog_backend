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
            user = await self.get_by_id(user_id)
            if not user:
                return False

            role_result = await self.db_session.execute(
                select(Role).where(Role.name == role_name)
            )
            role = role_result.scalar_one_or_none()

            if role and role not in user.roles:
                user.roles.append(role)
                await self.db_session.commit()
                return True

            return False

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Error adding role {role_name} to user {user_id}: {e}")
            return False

    async def get_user_roles(self, user_id: int) -> List[str]:
        """Получить роли пользователя"""
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return []
            return [role.name for role in user.roles]
        except SQLAlchemyError as e:
            logger.error(f"Error getting roles for user {user_id}: {e}")
            return []