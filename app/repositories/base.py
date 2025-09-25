from typing import cast, Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.models.base import Base

logger = logging.getLogger(__name__)
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий с CRUD операциями"""

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get_by_id(self, item_id: int) -> Optional[ModelType]:
        """Получить по ID"""
        try:
            from sqlalchemy import Column
            id_column: Column = self.model.id
            stmt = select(self.model).where(id_column == item_id)
            result = await self.db_session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by id {item_id}: {e}")
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить все записи"""
        try:
            result = await self.db_session.execute(
                select(self.model).offset(skip).limit(limit)
            )
            return cast(List[ModelType], result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model.__name__}: {e}")
            return []

    async def create(self, **kwargs) -> Optional[ModelType]:
        """Создать запись"""
        try:
            instance = self.model(**kwargs)
            self.db_session.add(instance)
            return instance
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            return None

    async def update(self, item_id: int, **kwargs) -> Optional[ModelType]:
        """Обновить запись"""
        try:
            instance = await self.get_by_id(item_id)
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
            return instance
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Error updating {self.model.__name__} {item_id}: {e}")
            return None

    async def delete(self, item_id: int) -> bool:
        """Удалить запись (soft delete)"""
        try:
            instance = await self.get_by_id(item_id)
            if instance:
                instance.is_active = False
                return True
            return False
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            logger.error(f"Error deleting {self.model.__name__} {item_id}: {e}")
            return False