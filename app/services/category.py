from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


class CategoryService:
    """Сервис для работы с категориями"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.category_repo = CategoryRepository(db_session)

    async def create_category(self, category_data: CategoryCreate) -> tuple[bool, Optional[str]]:
        """Создание категории"""
        try:
            existing_category = await self.category_repo.get_by_slug(category_data.slug)
            if existing_category:
                return False, "Category with this slug already exists"

            category = await self.category_repo.create(**category_data.model_dump())
            if not category:
                return False, "Failed to create category"

            await self.db_session.commit()
            return True, None

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Database error during category creation: {e}")
            return False, "Database error"

    async def update_category(self, category_id: int, category_data: CategoryUpdate) -> tuple[bool, Optional[str]]:
        """Обновление категории"""
        try:
            if category_data.slug:
                existing_category = await self.category_repo.get_by_slug(category_data.slug)
                if existing_category and existing_category.id != category_id:
                    return False, "Category with this slug already exists"

            category = await self.category_repo.update(category_id, **category_data.model_dump(exclude_unset=True))
            if not category:
                return False, "Category not found"

            await self.db_session.commit()
            return True, None

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Database error during category update: {e}")
            return False, "Database error"

    async def delete_category(self, category_id: int) -> tuple[bool, Optional[str]]:
        """Удаление категории (soft delete)"""
        try:
            category = await self.category_repo.get_by_id(category_id)
            if not category:
                return False, "Category not found"

            if category.posts:
                return False, "Cannot delete category with associated posts"

            success = await self.category_repo.delete(category_id)
            if not success:
                return False, "Failed to delete category"

            await self.db_session.commit()
            return True, None

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Database error during category deletion: {e}")
            return False, "Database error"