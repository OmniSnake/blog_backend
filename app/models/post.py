from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel


class Post(BaseModel):
    """Модель поста блога"""

    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    excerpt: Mapped[str] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_html: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    category: Mapped["Category"] = relationship("Category", back_populates="posts")
    author: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<Post {self.title}>"