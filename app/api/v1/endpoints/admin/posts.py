from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import require_admin
from app.schemas.post import PostCreate, PostUpdate, PostResponse, PostListResponse
from app.services.post import PostService

router = APIRouter()


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
        post_data: PostCreate,
        current_user: dict = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Создание нового поста (только для администраторов)"""
    post_service = PostService(db)
    success, error = await post_service.create_post(current_user["id"], post_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    post = await post_service.post_repo.get_by_slug(post_data.slug)
    return post


@router.get("/", response_model=PostListResponse)
async def get_posts(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        current_user: dict = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Получение списка постов (только для администраторов)"""
    post_service = PostService(db)
    posts = await post_service.post_repo.get_all(skip=skip, limit=limit)
    total = len(posts)

    return PostListResponse(
        posts=posts,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
        post_id: int,
        current_user: dict = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Получение поста по ID (только для администраторов)"""
    post_service = PostService(db)
    post = await post_service.post_repo.get_by_id(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
        post_id: int,
        post_data: PostUpdate,
        current_user: dict = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Обновление поста (только для администраторов)"""
    post_service = PostService(db)
    success, error = await post_service.update_post(post_id, post_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    post = await post_service.post_repo.get_by_id(post_id)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_id: int,
        current_user: dict = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    """Удаление поста (только для администраторов)"""
    post_service = PostService(db)
    success, error = await post_service.delete_post(post_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )