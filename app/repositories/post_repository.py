from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.post import Post
from app.models.category import Category
from app.repositories.base import PostRepositoryInterface

logger = logging.getLogger(__name__)


class PostRepository(PostRepositoryInterface[Post]):
    """Конкретная реализация репозитория постов (только данные)"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self._model = Post

    async def get_by_id(self, post_id: int) -> Optional[Post]:
        """Получить пост по ID"""
        try:
            result = await self._db_session.execute(
                select(Post).where(Post.id == post_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Error getting post by id {post_id}: {error}")
            return None

    async def get_by_slug(self, slug: str) -> Optional[Post]:
        """Получить пост по slug"""
        try:
            result = await self._db_session.execute(
                select(Post)
                .options(selectinload(Post.category), selectinload(Post.author))
                .where(Post.slug == slug)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Error getting post by slug {slug}: {error}")
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Post]:
        """Получить все посты"""
        try:
            result = await self._db_session.execute(
                select(Post).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except SQLAlchemyError as error:
            logger.error(f"Error getting all posts: {error}")
            return []

    async def get_published_posts(self, skip: int = 0, limit: int = 100) -> List[Post]:
        """Получить опубликованные посты"""
        try:
            result = await self._db_session.execute(
                select(Post)
                .options(selectinload(Post.category), selectinload(Post.author))
                .where(Post.is_published == True)
                .where(Post.is_active == True)
                .offset(skip)
                .limit(limit)
                .order_by(Post.created_at.desc())
            )
            return result.scalars().all()
        except SQLAlchemyError as error:
            logger.error(f"Error getting published posts: {error}")
            return []

    async def get_posts_by_category(self, category_slug: str, skip: int = 0, limit: int = 100) -> List[Post]:
        """Получить посты по категории"""
        try:
            result = await self._db_session.execute(
                select(Post)
                .join(Category)
                .options(selectinload(Post.category), selectinload(Post.author))
                .where(Category.slug == category_slug)
                .where(Post.is_published == True)
                .where(Post.is_active == True)
                .offset(skip)
                .limit(limit)
                .order_by(Post.created_at.desc())
            )
            return result.scalars().all()
        except SQLAlchemyError as error:
            logger.error(f"Error getting posts by category {category_slug}: {error}")
            return []

    async def create(self, **kwargs) -> Optional[Post]:
        """Создать пост"""
        try:
            post = Post(**kwargs)
            self._db_session.add(post)
            return post
        except SQLAlchemyError as error:
            logger.error(f"Error creating post: {error}")
            return None

    async def create_with_author(self, author_id: int, **kwargs) -> Optional[Post]:
        """Создать пост с автором"""
        try:
            post = Post(author_id=author_id, **kwargs)
            self._db_session.add(post)
            return post
        except SQLAlchemyError as error:
            logger.error(f"Error creating post with author: {error}")
            return None

    async def update(self, post_id: int, **kwargs) -> Optional[Post]:
        """Обновить пост"""
        try:
            post = await self.get_by_id(post_id)
            if post:
                for key, value in kwargs.items():
                    if hasattr(post, key):
                        setattr(post, key, value)
            return post
        except SQLAlchemyError as error:
            logger.error(f"Error updating post {post_id}: {error}")
            return None

    async def delete(self, post_id: int) -> bool:
        """Удалить пост (soft delete)"""
        try:
            post = await self.get_by_id(post_id)
            if post:
                post.is_active = False
                return True
            return False
        except SQLAlchemyError as error:
            logger.error(f"Error deleting post {post_id}: {error}")
            return False