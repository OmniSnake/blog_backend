from typing import Optional, List
from datetime import UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.refresh_token import RefreshToken
from app.repositories.base import RefreshTokenRepositoryInterface

logger = logging.getLogger(__name__)


class RefreshTokenRepository(RefreshTokenRepositoryInterface[RefreshToken]):
    """Конкретная реализация репозитория refresh токенов (только данные)"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session)
        self._model = RefreshToken

    async def get_by_id(self, token_id: int) -> Optional[RefreshToken]:
        """Получить токен по ID"""
        try:
            result = await self._db_session.execute(
                select(RefreshToken).where(RefreshToken.id == token_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Error getting token by id {token_id}: {error}")
            return None

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Получить токен по значению"""
        try:
            result = await self._db_session.execute(
                select(RefreshToken).where(RefreshToken.token == token)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as error:
            logger.error(f"Error getting token by value: {error}")
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[RefreshToken]:
        """Получить все токены"""
        try:
            result = await self._db_session.execute(
                select(RefreshToken).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except SQLAlchemyError as error:
            logger.error(f"Error getting all tokens: {error}")
            return []

    async def create(self, **kwargs) -> Optional[RefreshToken]:
        """Создать токен"""
        try:
            token = RefreshToken(**kwargs)
            self._db_session.add(token)
            return token
        except SQLAlchemyError as error:
            logger.error(f"Error creating token: {error}")
            return None

    async def update(self, token_id: int, **kwargs) -> Optional[RefreshToken]:
        """Обновить токен"""
        try:
            token = await self.get_by_id(token_id)
            if token:
                for key, value in kwargs.items():
                    if hasattr(token, key):
                        setattr(token, key, value)
            return token
        except SQLAlchemyError as error:
            logger.error(f"Error updating token {token_id}: {error}")
            return None

    async def delete(self, token_id: int) -> bool:
        """Удалить токен"""
        try:
            token = await self.get_by_id(token_id)
            if token:
                await self._db_session.delete(token)
                return True
            return False
        except SQLAlchemyError as error:
            logger.error(f"Error deleting token {token_id}: {error}")
            return False

    async def delete_expired_tokens(self) -> int:
        """Удалить просроченные токены"""
        try:
            from datetime import datetime
            result = await self._db_session.execute(
                select(RefreshToken).where(RefreshToken.expires_at < datetime.now(UTC))
            )
            expired_tokens = result.scalars().all()

            for token in expired_tokens:
                await self._db_session.delete(token)

            await self._db_session.commit()
            return len(expired_tokens)
        except SQLAlchemyError as error:
            logger.error(f"Error deleting expired tokens: {error}")
            return 0