from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar('ModelType')


class BaseRepository(Generic[ModelType], ABC):
    """Абстрактный базовый репозиторий с CRUD операциями"""

    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    @abstractmethod
    async def get_by_id(self, item_id: int) -> Optional[ModelType]:
        """Получить сущность по ID"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить все сущности"""
        pass

    @abstractmethod
    async def create(self, **kwargs) -> Optional[ModelType]:
        """Создать сущность"""
        pass

    @abstractmethod
    async def update(self, item_id: int, **kwargs) -> Optional[ModelType]:
        """Обновить сущность"""
        pass

    @abstractmethod
    async def delete(self, item_id: int) -> bool:
        """Удалить сущность"""
        pass


class UserRepositoryInterface(BaseRepository[ModelType], ABC):
    """Абстрактный репозиторий для пользователей"""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[ModelType]:
        """Получить пользователя по email"""
        pass

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Проверить существование email"""
        pass

    @abstractmethod
    async def get_with_roles(self, user_id: int) -> Optional[ModelType]:
        """Получить пользователя с ролями"""
        pass


class RoleRepositoryInterface(BaseRepository[ModelType], ABC):
    """Абстрактный репозиторий для ролей"""

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[ModelType]:
        """Получить роль по имени"""
        pass


class CategoryRepositoryInterface(BaseRepository[ModelType], ABC):
    """Абстрактный репозиторий для категорий"""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[ModelType]:
        """Получить категорию по slug"""
        pass

    @abstractmethod
    async def slug_exists(self, slug: str) -> bool:
        """Проверить существование slug"""
        pass

    @abstractmethod
    async def get_all_active(self) -> List[ModelType]:
        """Получить все активные категории"""
        pass


class PostRepositoryInterface(BaseRepository[ModelType], ABC):
    """Абстрактный репозиторий для постов"""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[ModelType]:
        """Получить пост по slug"""
        pass

    @abstractmethod
    async def get_published_posts(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить опубликованные посты"""
        pass

    @abstractmethod
    async def get_posts_by_category(self, category_slug: str, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить посты по категории"""
        pass

    @abstractmethod
    async def create_with_author(self, author_id: int, **kwargs) -> Optional[ModelType]:
        """Создать пост с автором"""
        pass


class RefreshTokenRepositoryInterface(BaseRepository[ModelType], ABC):
    """Абстрактный репозиторий для refresh токенов"""

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[ModelType]:
        """Получить токен по значению"""
        pass

    @abstractmethod
    async def delete_expired_tokens(self) -> int:
        """Удалить просроченные токены"""
        pass