from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING
from datetime import datetime
from .base import Base

if TYPE_CHECKING:
    from .user import User

class RefreshToken(Base):
    """Модель refresh токена"""

    __tablename__ = "refresh_tokens"

    token: str = Column(String(512), unique=True, index=True, nullable=False)
    expires_at: datetime = Column(DateTime, nullable=False)
    user_id: int = Column(ForeignKey("users.id"), nullable=False)

    user: 'User' = relationship('User', back_populates='refresh_tokens')

    def __repr__(self) -> str:
        return f"<RefreshToken {self.token[:10]}...>"