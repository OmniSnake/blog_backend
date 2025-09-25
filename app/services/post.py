from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.repositories.post import PostRepository
from app.repositories.category import CategoryRepository
from app.schemas.post import PostCreate, PostUpdate

logger = logging.getLogger(__name__)


class PostService:
    """Сервис для работы с постами"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.post_repo = PostRepository(db_session)
        self.category_repo = CategoryRepository(db_session)

    async def create_post(self, author_id: int, post_data: PostCreate) -> Tuple[bool, Optional[str]]:
        """Создание поста"""
        try:
            category = await self.category_repo.get_by_id(post_data.category_id)
            if not category:
                return False, "Category not found"

            existing_post = await self.post_repo.get_by_slug(post_data.slug)
            if existing_post:
                return False, "Post with this slug already exists"

            post = await self.post_repo.create_with_author(author_id, **post_data.model_dump())
            if not post:
                return False, "Failed to create post"

            await self.db_session.commit()
            return True, None

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Database error during post creation: {e}")
            return False, "Database error"

    async def update_post(self, post_id: int, post_data: PostUpdate) -> Tuple[bool, Optional[str]]:
        """Обновление поста"""
        try:
            if post_data.slug:
                existing_post = await self.post_repo.get_by_slug(post_data.slug)
                if existing_post and existing_post.id != post_id:
                    return False, "Post with this slug already exists"

            if post_data.category_id:
                category = await self.category_repo.get_by_id(post_data.category_id)
                if not category:
                    return False, "Category not found"

            post = await self.post_repo.update(post_id, **post_data.model_dump(exclude_unset=True))
            if not post:
                return False, "Post not found"

            await self.db_session.commit()
            return True, None

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Database error during post update: {e}")
            return False, "Database error"

    async def delete_post(self, post_id: int) -> Tuple[bool, Optional[str]]:
        """Удаление поста (soft delete)"""
        try:
            success = await self.post_repo.delete(post_id)
            if not success:
                return False, "Post not found"

            await self.db_session.commit()
            return True, None

        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Database error during post deletion: {e}")
            return False, "Database error"