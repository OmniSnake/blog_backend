from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.post import Post
from app.models.category import Category
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PostRepository(BaseRepository[Post]):
    """Репозиторий для постов"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(Post, db_session)

    async def get_by_slug(self, slug: str) -> Optional[Post]:
        """Получить пост по slug"""
        try:
            result = await self.db_session.execute(
                select(Post)
                .options(selectinload(Post.category), selectinload(Post.author))
                .where(Post.slug == slug)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting post by slug {slug}: {e}")
            return None

    async def get_published_posts(self, skip: int = 0, limit: int = 100) -> List[Post]:
        """Получить опубликованные посты"""
        try:
            result = await self.db_session.execute(
                select(Post)
                .options(selectinload(Post.category), selectinload(Post.author))
                .where(Post.is_published == True)
                .where(Post.is_active == True)
                .offset(skip)
                .limit(limit)
                .order_by(Post.created_at.desc())
            )
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting published posts: {e}")
            return []

    async def get_posts_by_category(self, category_slug: str, skip: int = 0, limit: int = 100) -> List[Post]:
        """Получить посты по категории"""
        try:
            result = await self.db_session.execute(
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
        except SQLAlchemyError as e:
            logger.error(f"Error getting posts by category {category_slug}: {e}")
            return []

    async def create_with_author(self, author_id: int, **kwargs) -> Optional[Post]:
        """Создать пост с автором"""
        try:
            instance = self.model(author_id=author_id, **kwargs)
            self.db_session.add(instance)
            return instance
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Error creating post: {e}")
            return None