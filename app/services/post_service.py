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
    """Сервис для работы с постами"""

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
        """Создание поста с санитизацией контента"""
        try:
            category = await self._category_repository.get_by_id(post_data.category_id)
            if not category:
                return False, "Category not found"

            existing_post = await self._post_repository.get_by_slug(post_data.slug)
            if existing_post:
                return False, "Post with this slug already exists"

            sanitized_content = Post.sanitize_html(post_data.content)

            post_dict = post_data.model_dump()
            post_dict['content'] = sanitized_content
            post_dict['author_id'] = author_id

            post = await self._post_repository.create(**post_dict)
            if not post:
                return False, "Failed to create post"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during post creation: {error}")
            return False, "Database error"

    async def update_post(self, post_id: int, post_data: PostUpdate) -> Tuple[bool, Optional[str]]:
        """Обновление поста с санитизацией контента"""
        try:
            update_data = post_data.model_dump(exclude_unset=True)

            if 'slug' in update_data:
                existing_post = await self._post_repository.get_by_slug(update_data['slug'])
                if existing_post and existing_post.id != post_id:
                    return False, "Post with this slug already exists"

            if 'category_id' in update_data:
                category = await self._category_repository.get_by_id(update_data['category_id'])
                if not category:
                    return False, "Category not found"

            if 'content' in update_data:
                update_data['content'] = Post.sanitize_html(update_data['content'])

            post = await self._post_repository.update(post_id, **update_data)
            if not post:
                return False, "Post not found"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during post update: {error}")
            return False, "Database error"

    async def delete_post(self, post_id: int) -> Tuple[bool, Optional[str]]:
        """Удаление поста"""
        try:
            success = await self._post_repository.delete(post_id)
            if not success:
                return False, "Post not found"

            await self._db_session.commit()
            return True, None

        except SQLAlchemyError as error:
            await self._db_session.rollback()
            logger.error(f"Database error during post deletion: {error}")
            return False, "Database error"