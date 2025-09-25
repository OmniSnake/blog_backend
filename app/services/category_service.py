from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.repositories.base import CategoryRepositoryInterface, PostRepositoryInterface
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.models.category import Category
from app.models.post import Post

logger = logging.getLogger(__name__)


class CategoryService:
    """Сервис для работы с категориями (чистая бизнес-логика)"""

    def __init__(
        self,
        category_repository: CategoryRepositoryInterface[Category],
        post_repository: PostRepositoryInterface[Post],
        db_session: AsyncSession
    ):
        self._category_repository = category_repository
        self._post_repository = post_repository
        self._db_session = db_session

    async def create_category(self, category_data: CategoryCreate) -> Tuple[bool, Optional[str]]:
        """Создание категории (бизнес-логика)"""
        try:
            if await self._category_repository.slug_exists(category_data.slug):
                return False, "Category with this slug already exists"

            category = await self._category_repository.create(**category_data.model_dump())
            if not category:
                return False, "Failed to create category"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during category creation: {error}")
            return False, "Database error"

    async def update_category(self, category_id: int, category_data: CategoryUpdate) -> Tuple[bool, Optional[str]]:
        """Обновление категории (бизнес-логика)"""
        try:
            if category_data.slug:
                existing_category = await self._category_repository.get_by_slug(category_data.slug)
                if existing_category and existing_category.id != category_id:
                    return False, "Category with this slug already exists"

            category = await self._category_repository.update(category_id, **category_data.model_dump(exclude_unset=True))
            if not category:
                return False, "Category not found"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during category update: {error}")
            return False, "Database error"

    async def delete_category(self, category_id: int) -> Tuple[bool, Optional[str]]:
        """Удаление категории (бизнес-логика)"""
        try:
            category = await self._category_repository.get_by_id(category_id)
            if not category:
                return False, "Category not found"

            has_posts = await self._post_repository.exists_by_category_id(category_id)
            if has_posts:
                return False, "Cannot delete category with associated posts"

            success = await self._category_repository.delete(category_id)
            if not success:
                return False, "Failed to delete category"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during category deletion: {error}")
            return False, "Database error"

    async def _get_posts_by_category(self, category_id: int) -> List[Post]:
        """Получить посты категории (внутренняя бизнес-логика)"""
        try:
            all_posts = await self._post_repository.get_all()
            return [post for post in all_posts if post.category_id == category_id and post.is_active]
        except Exception as error:
            logger.error(f"Error getting posts by category {category_id}: {error}")
            return []