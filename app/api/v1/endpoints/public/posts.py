from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.post_repository import PostRepository
from app.schemas.post import PostResponse, PostListResponse

router = APIRouter()


@router.get("/", response_model=PostListResponse)
async def get_posts(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=50),
        db: AsyncSession = Depends(get_db)
):
    """Получение списка опубликованных постов (публичный доступ)"""
    post_repository = PostRepository(db)
    posts = await post_repository.get_published_posts(skip=skip, limit=limit)

    return PostListResponse(
        posts=posts,
        total=len(posts),
        skip=skip,
        limit=limit
    )


@router.get("/{slug}", response_model=PostResponse)
async def get_post_by_slug(
        slug: str,
        db: AsyncSession = Depends(get_db)
):
    """Получение поста по slug (публичный доступ)"""
    post_repository = PostRepository(db)
    post = await post_repository.get_by_slug(slug)

    if not post or not post.is_published or not post.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post