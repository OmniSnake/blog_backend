from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RoleBase(BaseModel):
    """Базовая схема роли"""
    name: str
    description: Optional[str] = None
    permissions: Optional[str] = None


class RoleResponse(RoleBase):
    """Схема ответа роли"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True