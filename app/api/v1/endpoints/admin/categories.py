from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import require_admin
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import CategoryService
from typing import List

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
        category_data: CategoryCreate,
        current_user: dict = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Создание новой категории (только для администраторов)"""
    category_service = CategoryService(db)
    success, error = await category_service.create_category(category_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    category = await category_service.category_repo.get_by_slug(category_data.slug)
    return category


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        current_user: dict = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Получение списка категорий (только для администраторов)"""
    category_service = CategoryService(db)
    categories = await category_service.category_repo.get_all(skip=skip, limit=limit)
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
        category_id: int,
        current_user: dict = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Получение категории по ID (только для администраторов)"""
    category_service = CategoryService(db)
    category = await category_service.category_repo.get_by_id(category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
        category_id: int,
        category_data: CategoryUpdate,
        current_user: dict = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Обновление категории (только для администраторов)"""
    category_service = CategoryService(db)
    success, error = await category_service.update_category(category_id, category_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    category = await category_service.category_repo.get_by_id(category_id)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
        category_id: int,
        current_user: dict = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Удаление категории (только для администраторов)"""
    category_service = CategoryService(db)
    success, error = await category_service.delete_category(category_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )