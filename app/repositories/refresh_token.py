from typing import Optional
from datetime import UTC

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Репозиторий для refresh токенов"""

    def __init__(self, db_session: AsyncSession):
        super().__init__(RefreshToken, db_session)

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Получить токен по значению"""
        result = await self.db_session.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def delete_expired_tokens(self) -> int:
        """Удалить просроченные токены"""
        from datetime import datetime
        result = await self.db_session.execute(
            select(RefreshToken).where(RefreshToken.expires_at < datetime.now(UTC))
        )
        expired_tokens = result.scalars().all()

        for token in expired_tokens:
            await self.db_session.delete(token)

        await self.db_session.commit()
        return len(expired_tokens)