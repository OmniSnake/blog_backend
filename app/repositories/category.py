from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.category import Category
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class CategoryRepository(BaseRepository[Category]):
    """Репозиторий для категорий"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Category, db_session)

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """Получить категорию по slug"""
        try:
            result = await self.db_session.execute(
                select(Category).where(Category.slug == slug)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting category by slug {slug}: {e}")
            return None

    async def get_all_active(self) -> List[Category]:
        """Получить все активные категории"""
        try:
            result = await self.db_session.execute(
                select(Category).where(Category.is_active == True)
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting active categories: {e}")
            return []