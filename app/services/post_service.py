from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.repositories.base import PostRepositoryInterface, CategoryRepositoryInterface
from app.schemas.post import PostCreate, PostUpdate
from app.models.post import Post
from app.models.category import Category

logger = logging.getLogger(__name__)


class PostService:
    """Сервис для работы с постами (чистая бизнес-логика)"""

    def __init__(
        self,
        post_repository: PostRepositoryInterface[Post],
        category_repository: CategoryRepositoryInterface[Category],
        db_session: AsyncSession
    ):
        self._post_repository = post_repository
        self._category_repository = category_repository
        self._db_session = db_session

    async def create_post(self, author_id: int, post_data: PostCreate) -> Tuple[bool, Optional[str]]:
        """Создание поста (бизнес-логика)"""
        try:
            category = await self._category_repository.get_by_id(post_data.category_id)
            if not category:
                return False, "Category not found"

            existing_post = await self._post_repository.get_by_slug(post_data.slug)
            if existing_post:
                return False, "Post with this slug already exists"

            post = await self._post_repository.create_with_author(author_id, **post_data.model_dump())
            if not post:
                return False, "Failed to create post"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during post creation: {error}")
            return False, "Database error"

    async def update_post(self, post_id: int, post_data: PostUpdate) -> Tuple[bool, Optional[str]]:
        """Обновление поста (бизнес-логика)"""
        try:
            if post_data.slug:
                existing_post = await self._post_repository.get_by_slug(post_data.slug)
                if existing_post and existing_post.id != post_id:
                    return False, "Post with this slug already exists"

            if post_data.category_id:
                category = await self._category_repository.get_by_id(post_data.category_id)
                if not category:
                    return False, "Category not found"

            post = await self._post_repository.update(post_id, **post_data.model_dump(exclude_unset=True))
            if not post:
                return False, "Post not found"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during post update: {error}")
            return False, "Database error"

    async def delete_post(self, post_id: int) -> Tuple[bool, Optional[str]]:
        """Удаление поста (бизнес-логика)"""
        try:
            post = await self._post_repository.get_by_id(post_id)
            if not post:
                return False, "Post not found"

            success = await self._post_repository.delete(post_id)
            if not success:
                return False, "Failed to delete post"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during post deletion: {error}")
            return False, "Database error"