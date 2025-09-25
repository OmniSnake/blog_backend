from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.category_repository import CategoryRepository
from app.repositories.post_repository import PostRepository
from app.schemas.category import CategoryResponse
from app.schemas.post import PostListResponse
from typing import List

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
        db: AsyncSession = Depends(get_db)
):
    """Получение списка категорий (публичный доступ)"""
    category_repository = CategoryRepository(db)
    categories = await category_repository.get_all_active()
    return categories


@router.get("/{slug}/posts", response_model=PostListResponse)
async def get_posts_by_category(
        slug: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=50),
        db: AsyncSession = Depends(get_db)
):
    """Получение постов по категории (публичный доступ)"""
    category_repository = CategoryRepository(db)
    post_repository = PostRepository(db)

    category = await category_repository.get_by_slug(slug)
    if not category or not category.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    posts = await post_repository.get_posts_by_category(slug, skip=skip, limit=limit)

    return PostListResponse(
        posts=posts,
        total=len(posts),
        skip=skip,
        limit=limit
    )