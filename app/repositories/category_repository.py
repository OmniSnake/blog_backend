from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.category import Category
from app.repositories.base import CategoryRepositoryInterface

logger = logging.getLogger(__name__)


class CategoryRepository(CategoryRepositoryInterface[Category]):
    """Конкретная реализация репозитория категорий (только данные)"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self._model = Category

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """Получить категорию по ID"""
        try:
            result = await self._db_session.execute(
                select(Category).where(Category.id == category_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Error getting category by id {category_id}: {error}")
            return None

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """Получить категорию по slug"""
        try:
            result = await self._db_session.execute(
                select(Category).where(Category.slug == slug)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Error getting category by slug {slug}: {error}")
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """Получить все категории"""
        try:
            result = await self._db_session.execute(
                select(Category).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except SQLAlchemyError as error:
            logger.error(f"Error getting all categories: {error}")
            return []

    async def get_all_active(self) -> List[Category]:
        """Получить все активные категории"""
        try:
            result = await self._db_session.execute(
                select(Category).where(Category.is_active == True)
            )
            return result.scalars().all()
        except SQLAlchemyError as error:
            logger.error(f"Error getting active categories: {error}")
            return []

    async def slug_exists(self, slug: str) -> bool:
        """Проверить существование slug"""
        try:
            result = await self._db_session.execute(
                select(Category.id).where(Category.slug == slug)
            )
            return result.scalar() is not None
        except SQLAlchemyError as error:
            logger.error(f"Error checking slug existence {slug}: {error}")
            return False

    async def create(self, **kwargs) -> Optional[Category]:
        """Создать категорию"""
        try:
            category = Category(**kwargs)
            self._db_session.add(category)
            return category
        except SQLAlchemyError as error:
            logger.error(f"Error creating category: {error}")
            return None

    async def update(self, category_id: int, **kwargs) -> Optional[Category]:
        """Обновить категорию"""
        try:
            category = await self.get_by_id(category_id)
            if category:
                for key, value in kwargs.items():
                    if hasattr(category, key):
                        setattr(category, key, value)
            return category
        except SQLAlchemyError as error:
            logger.error(f"Error updating category {category_id}: {error}")
            return None

    async def delete(self, category_id: int) -> bool:
        """Удалить категорию (soft delete)"""
        try:
            category = await self.get_by_id(category_id)
            if category:
                category.is_active = False
                return True
            return False
        except SQLAlchemyError as error:
            logger.error(f"Error deleting category {category_id}: {error}")
            return False