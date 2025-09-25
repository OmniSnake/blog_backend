from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class BaseModel(Base):
    """Базовая модель с общими полями"""
    __abstract__ = True

    id: int = Column(Integer, primary_key=True, index=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), onupdate=func.now())
    is_active: bool = Column(Boolean, default=True)