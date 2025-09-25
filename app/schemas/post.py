from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re
from .user import UserResponse
from .category import CategoryResponse


class PostBase(BaseModel):
    """Базовая схема поста"""
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    is_published: bool = False
    category_id: int

    @field_validator('slug')
    def validate_slug(cls, v):
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers and hyphens')
        return v

    @field_validator('title')
    def validate_title_length(cls, v):
        if len(v) < 3:
            raise ValueError('Title must be at least 3 characters long')
        if len(v) > 200:
            raise ValueError('Title must not exceed 200 characters')
        return v


class PostCreate(PostBase):
    """Схема для создания поста"""
    pass


class PostUpdate(BaseModel):
    """Схема для обновления поста"""
    title: Optional[str] = None
    slug: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    is_published: Optional[bool] = None
    category_id: Optional[int] = None

    @field_validator('slug')
    def validate_slug(cls, v):
        if v is not None and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers and hyphens')
        return v

    @field_validator('title')
    def validate_title_length(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError('Title must be at least 3 characters long')
            if len(v) > 200:
                raise ValueError('Title must not exceed 200 characters')
        return v


class PostResponse(PostBase):
    """Схема ответа поста"""
    id: int
    content_html: str
    author: UserResponse
    category: CategoryResponse
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """Схема для списка постов"""
    posts: list[PostResponse]
    total: int
    skip: int
    limit: int