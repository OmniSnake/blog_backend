from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings


class DatabaseManager:
    """Менеджер базы данных"""

    def __init__(self) -> None:
        self.engine = create_async_engine(
            settings.DATABASE_URL,
            echo=True,
            future=True
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получить асинхронную сессию как генератор"""
        async with self.async_session() as session:
            try:
                yield session
            finally:
                await session.close()


db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для получения сессии БД"""
    async for session in db_manager.get_session():
        yield session