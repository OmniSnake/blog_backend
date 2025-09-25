from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.repositories.base import UserRepositoryInterface, RoleRepositoryInterface
from app.schemas.user import UserRoleUpdate
from app.models.role import user_role_association, Role
from app.models.user import User

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для управления пользователями (чистая бизнес-логика)"""

    def __init__(
            self,
            user_repository: UserRepositoryInterface[User],
            role_repository: RoleRepositoryInterface[Role],
            db_session: AsyncSession
    ):
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._db_session = db_session

    async def update_user_roles(self, user_id: int, roles_data: UserRoleUpdate) -> Tuple[bool, Optional[str]]:
        """Обновить роли пользователя (бизнес-логика)"""
        try:
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                return False, "User not found"

            available_roles = {}
            for role_name in roles_data.roles:
                role = await self._role_repository.get_by_name(role_name)
                if role:
                    available_roles[role_name] = role
                else:
                    return False, f"Role '{role_name}' not found"

            user_with_roles = await self._user_repository.get_with_roles(user_id)
            if not user_with_roles:
                return False, "Failed to get user roles"

            current_roles = [role.name for role in user_with_roles.roles]

            for role_name in current_roles:
                if role_name not in roles_data.roles:
                    success = await self._remove_role_from_user(user_id, role_name)
                    if not success:
                        logger.warning(f"Failed to remove role '{role_name}' from user {user_id}")

            for role_name in roles_data.roles:
                if role_name not in current_roles:
                    success = await self._add_role_to_user(user_id, role_name)
                    if not success:
                        return False, f"Failed to add role '{role_name}'"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during user roles update: {error}")
            return False, "Database error"

    async def deactivate_user(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """Деактивировать пользователя (бизнес-логика)"""
        try:
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                return False, "User not found"

            success = await self._user_repository.delete(user_id)
            if not success:
                return False, "Failed to deactivate user"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during user deactivation: {error}")
            return False, "Database error"

    async def _add_role_to_user(self, user_id: int, role_name: str) -> bool:
        """Добавить роль пользователю (внутренняя бизнес-логика)"""
        try:
            user = await self._user_repository.get_with_roles(user_id)
            role = await self._role_repository.get_by_name(role_name)

            if not user or not role:
                return False

            if role not in user.roles:
                user.roles.append(role)
                self._db_session.add(user)
                return True

            return False

        except SQLAlchemyError as error:
            logger.error(f"Error adding role {role_name} to user {user_id}: {error}")
            return False

    async def _remove_role_from_user(self, user_id: int, role_name: str) -> bool:
        """Удалить роль у пользователя (внутренняя бизнес-логика)"""
        try:
            from sqlalchemy import delete

            role = await self._role_repository.get_by_name(role_name)
            if not role:
                return False

            stmt = delete(user_role_association).where(
                user_role_association.c.user_id == user_id,
                user_role_association.c.role_id == role.id
            )
            await self._db_session.execute(stmt)
            return True

        except SQLAlchemyError as error:
            logger.error(f"Error removing role {role_name} from user {user_id}: {error}")
            return False

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