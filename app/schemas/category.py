from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re


class CategoryBase(BaseModel):
    """Базовая схема категории"""
    name: str
    slug: str
    description: Optional[str] = None

    @field_validator('slug')
    def validate_slug(cls, v):
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers and hyphens')
        return v


class CategoryCreate(CategoryBase):
    """Схема для создания категории"""
    pass


class CategoryUpdate(BaseModel):
    """Схема для обновления категории"""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None

    @field_validator('slug')
    def validate_slug(cls, v):
        if v is not None and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers and hyphens')
        return v


class CategoryResponse(CategoryBase):
    """Схема ответа категории"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)