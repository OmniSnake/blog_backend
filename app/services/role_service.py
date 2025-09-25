from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.repositories.base import UserRepositoryInterface, RoleRepositoryInterface
from app.models.user import User
from app.models.role import Role, user_role_association

logger = logging.getLogger(__name__)


class RoleService:
    """Сервис для управления ролями пользователей (чистая бизнес-логика)"""

    def __init__(
            self,
            user_repository: UserRepositoryInterface[User],
            role_repository: RoleRepositoryInterface[Role],
            db_session: AsyncSession
    ):
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._db_session = db_session

    async def assign_role_to_user(self, user_id: int, role_name: str) -> Tuple[bool, Optional[str]]:
        """Назначить роль пользователю (бизнес-логика)"""
        try:
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                return False, "User not found"

            role = await self._role_repository.get_by_name(role_name)
            if not role:
                return False, f"Role '{role_name}' not found"

            user_with_roles = await self._user_repository.get_with_roles(user_id)
            if not user_with_roles:
                return False, "Failed to get user roles"

            current_roles = [role.name for role in user_with_roles.roles]
            if role_name in current_roles:
                return False, f"User already has role '{role_name}'"

            success = await self._add_role_association(user_id, role.id)
            if not success:
                return False, "Failed to assign role"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during role assignment: {error}")
            return False, "Database error"

    async def remove_role_from_user(self, user_id: int, role_name: str) -> Tuple[bool, Optional[str]]:
        """Удалить роль у пользователя (бизнес-логика)"""
        try:
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                return False, "User not found"

            role = await self._role_repository.get_by_name(role_name)
            if not role:
                return False, f"Role '{role_name}' not found"

            user_with_roles = await self._user_repository.get_with_roles(user_id)
            if not user_with_roles:
                return False, "Failed to get user roles"

            current_roles = [role.name for role in user_with_roles.roles]
            if role_name not in current_roles:
                return False, f"User does not have role '{role_name}'"

            success = await self._remove_role_association(user_id, role.id)
            if not success:
                return False, "Failed to remove role"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during role removal: {error}")
            return False, "Database error"

    async def get_user_roles(self, user_id: int) -> List[str]:
        """Получить роли пользователя (бизнес-логика)"""
        try:
            user = await self._user_repository.get_with_roles(user_id)
            if not user or not user.roles:
                return []
            return [role.name for role in user.roles]
        except SQLAlchemyError as error:
            logger.error(f"Error getting roles for user {user_id}: {error}")
            return []

    async def _add_role_association(self, user_id: int, role_id: int) -> bool:
        """Добавить связь пользователь-роль (внутренняя бизнес-логика)"""
        try:
            from sqlalchemy import insert

            stmt = insert(user_role_association).values(
                user_id=user_id,
                role_id=role_id
            )
            await self._db_session.execute(stmt)
            return True
        except SQLAlchemyError as error:
            logger.error(f"Error adding role association: {error}")
            return False

    async def _remove_role_association(self, user_id: int, role_id: int) -> bool:
        """Удалить связь пользователь-роль (внутренняя бизнес-логика)"""
        try:
            from sqlalchemy import delete

            stmt = delete(user_role_association).where(
                user_role_association.c.user_id == user_id,
                user_role_association.c.role_id == role_id
            )
            await self._db_session.execute(stmt)
            return True
        except SQLAlchemyError as error:
            logger.error(f"Error removing role association: {error}")
            return False