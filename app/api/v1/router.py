from fastapi import APIRouter
from app.api.v1.endpoints import auth, users
from app.api.v1.endpoints.public import posts as public_posts, categories as public_categories
from app.api.v1.endpoints.admin import categories as admin_categories, posts as admin_posts, users as admin_users

api_router = APIRouter()

api_router.include_router(public_posts.router, prefix="/posts", tags=["posts - public"])
api_router.include_router(public_categories.router, prefix="/categories", tags=["categories - public"])

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

api_router.include_router(users.router, prefix="/users", tags=["users"])

api_router.include_router(admin_categories.router, prefix="/admin/categories", tags=["categories - admin"])
api_router.include_router(admin_posts.router, prefix="/admin/posts", tags=["posts - admin"])
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["users - admin"])