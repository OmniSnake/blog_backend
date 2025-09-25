from sqlalchemy import Column, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from typing import List, TYPE_CHECKING
from .base import Base

if TYPE_CHECKING:
    from .user import User

user_role_association = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('role_id', ForeignKey('roles.id'), primary_key=True)
)


class Role(Base):
    """Модель роли пользователя"""

    __tablename__ = "roles"

    name: str = Column(String(50), unique=True, index=True, nullable=False)
    description: str = Column(Text, nullable=True)
    permissions: str = Column(Text, nullable=True)

    users: List['User'] = relationship(
        'User',
        secondary=user_role_association,
        back_populates='roles'
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


class RolePermissions:
    """Класс-константа для системных разрешений"""

    POST_CREATE = "post:create"
    POST_READ = "post:read"
    POST_UPDATE = "post:update"
    POST_DELETE = "post:delete"

    CATEGORY_CREATE = "category:create"
    CATEGORY_READ = "category:read"
    CATEGORY_UPDATE = "category:update"
    CATEGORY_DELETE = "category:delete"

    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    ADMIN_READ = "admin:read"
    ADMIN_UPDATE = "admin:update"

    @classmethod
    def get_role_permissions(cls, role_name: str) -> list[str]:
        """Получить разрешения для роли"""
        role_permissions_map = {
            "user": [cls.POST_READ, cls.CATEGORY_READ],
            "admin": [
                cls.POST_CREATE, cls.POST_READ, cls.POST_UPDATE, cls.POST_DELETE,
                cls.CATEGORY_CREATE, cls.CATEGORY_READ, cls.CATEGORY_UPDATE, cls.CATEGORY_DELETE,
                cls.USER_READ, cls.USER_UPDATE, cls.USER_DELETE,
                cls.ADMIN_READ, cls.ADMIN_UPDATE
            ]
        }
        return role_permissions_map.get(role_name, [])