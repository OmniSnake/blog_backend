from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import bleach
from .base import BaseModel


class Post(BaseModel):
    """Модель поста блога"""

    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    excerpt: Mapped[str] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    category: Mapped["Category"] = relationship("Category", back_populates="posts", lazy="selectin")
    author: Mapped["User"] = relationship("User", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Post {self.title}>"

    @staticmethod
    def sanitize_html(content: str) -> str:
        """Санитизация HTML контента"""
        allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'h1', 'h2', 'h3', 'h4', 'blockquote', 'code',
                        'pre']
        allowed_attributes = {'a': ['href', 'title'], 'img': ['alt']}

        return bleach.clean(
            content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )