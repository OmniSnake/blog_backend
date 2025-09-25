from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from .base import BaseModel


class Category(BaseModel):
    """Модель категории поста"""

    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    posts: Mapped[List["Post"]] = relationship("Post", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category {self.name}>"