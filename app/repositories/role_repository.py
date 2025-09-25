from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.role import Role
from app.repositories.base import RoleRepositoryInterface

logger = logging.getLogger(__name__)


class RoleRepository(RoleRepositoryInterface[Role]):
    """Конкретная реализация репозитория ролей (только данные)"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self._model = Role

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        """Получить роль по ID"""
        try:
            result = await self._db_session.execute(
                select(Role).where(Role.id == role_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Error getting role by id {role_id}: {error}")
            return None

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Получить роль по имени"""
        try:
            result = await self._db_session.execute(
                select(Role).where(Role.name == name)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Error getting role by name {name}: {error}")
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """Получить все роли"""
        try:
            result = await self._db_session.execute(
                select(Role).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except SQLAlchemyError as error:
            logger.error(f"Error getting all roles: {error}")
            return []

    async def create(self, **kwargs) -> Optional[Role]:
        """Создать роль"""
        try:
            role = Role(**kwargs)
            self._db_session.add(role)
            return role
        except SQLAlchemyError as error:
            logger.error(f"Error creating role: {error}")
            return None

    async def update(self, role_id: int, **kwargs) -> Optional[Role]:
        """Обновить роль"""
        try:
            role = await self.get_by_id(role_id)
            if role:
                for key, value in kwargs.items():
                    if hasattr(role, key):
                        setattr(role, key, value)
            return role
        except SQLAlchemyError as error:
            logger.error(f"Error updating role {role_id}: {error}")
            return None

    async def delete(self, role_id: int) -> bool:
        """Удалить роль (soft delete)"""
        try:
            role = await self.get_by_id(role_id)
            if role:
                role.is_active = False
                return True
            return False
        except SQLAlchemyError as error:
            logger.error(f"Error deleting role {role_id}: {error}")
            return False