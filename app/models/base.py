from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from datetime import datetime


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class BaseModel(Base):
    """Базовая модель с общими полями"""
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),onupdate=func.now(),nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)