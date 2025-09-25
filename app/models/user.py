from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from typing import List, TYPE_CHECKING
from .base import Base
from .refresh_token import RefreshToken

if TYPE_CHECKING:
    from .role import Role


class User(Base):
    """Модель пользователя"""

    __tablename__ = "users"

    email: str = Column(String(255), unique=True, index=True, nullable=False)
    password_hash: str = Column(String(255), nullable=False)
    first_name: str = Column(String(100), nullable=True)
    last_name: str = Column(String(100), nullable=True)
    is_verified: bool = Column(Boolean, default=False)

    roles: List['Role'] = relationship(
        'Role',
        secondary='user_roles',
        back_populates='users'
    )
    refresh_tokens: List['RefreshToken'] = relationship('RefreshToken', back_populates='user')

    def __repr__(self) -> str:
        return f"<User {self.email}>"