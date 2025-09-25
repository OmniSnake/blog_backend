from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Репозиторий для ролей"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Role, db_session)

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Получить роль по имени"""
        result = await self.db_session.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()