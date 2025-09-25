from typing import Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, delete
import logging
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.schemas.user import UserRoleUpdate
from app.models.role import Role, user_role_association

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для управления пользователями"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.user_repo = UserRepository(db_session)
        self.role_repo = RoleRepository(db_session)

    async def update_user_roles(self, user_id: int, roles_data: UserRoleUpdate) -> Tuple[bool, Optional[str]]:
        """Обновление ролей пользователя"""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return False, "User not found"

            available_roles = {}
            for role_name in roles_data.roles:
                role = await self.role_repo.get_by_name(role_name)
                if role:
                    available_roles[role_name] = role
                else:
                    return False, f"Role '{role_name}' not found"

            current_roles = await self.user_repo.get_user_roles(user_id)

            for role_name in current_roles:
                if role_name not in roles_data.roles:
                    success = await self._remove_role_from_user(user_id, role_name)
                    if not success:
                        logger.warning(f"Failed to remove role '{role_name}' from user {user_id}")

            for role_name in roles_data.roles:
                if role_name not in current_roles:
                    success = await self.user_repo.add_role_to_user(user_id, role_name)
                    if not success:
                        return False, f"Failed to add role '{role_name}'"

            await self.db_session.commit()
            return True, None

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Database error during user roles update: {e}")
            return False, "Database error"

    async def _remove_role_from_user(self, user_id: int, role_name: str) -> bool:
        """Удаление роли у пользователя"""
        try:
            role_result = await self.db_session.execute(
                select(Role.id).where(Role.name == role_name)
            )
            role_id = role_result.scalar_one_or_none()

            if not role_id:
                logger.error(f"Role '{role_name}' not found")
                return False

            stmt = delete(user_role_association).where(
                user_role_association.c.user_id == user_id,
                user_role_association.c.role_id == role_id
            )
            await self.db_session.execute(stmt)
            return True

        except SQLAlchemyError as e:
            logger.error(f"Error removing role {role_name} from user {user_id}: {e}")
            return False

    async def deactivate_user(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """Деактивация пользователя"""
        try:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                return False, "User not found"

            success = await self.user_repo.delete(user_id)
            if not success:
                return False, "Failed to deactivate user"

            await self.db_session.commit()
            return True, None

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Database error during user deactivation: {e}")
            return False, "Database error"