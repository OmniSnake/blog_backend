import pytest
from httpx import AsyncClient


class TestPostsAPI:
    async def test_get_posts_public(self, client, test_category, test_user, session):
        """Test getting public posts."""
        from app.repositories.post_repository import PostRepository

        post_repo = PostRepository(session)
        await post_repo.create(
            title="Public Post",
            slug="public-post",
            content="Public content",
            category_id=test_category.id,
            author_id=test_user.id,
            is_published=True
        )
        await session.commit()

        response = await client.get("/api/v1/posts/")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert len(data["posts"]) > 0

    async def test_get_post_by_slug_public(self, client, test_category, test_user, session):
        """Test getting a specific post by slug."""
        from app.repositories.post_repository import PostRepository

        post_repo = PostRepository(session)
        await post_repo.create(
            title="Specific Post",
            slug="specific-post",
            content="Specific content",
            category_id=test_category.id,
            author_id=test_user.id,
            is_published=True
        )
        await session.commit()

        response = await client.get("/api/v1/posts/specific-post")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "specific-post"
        assert data["title"] == "Specific Post"

    async def test_get_post_not_found(self, client):
        """Test getting a non-existent post."""
        response = await client.get("/api/v1/posts/non-existent-slug")
        assert response.status_code == 404

    async def test_create_post_unauthorized(self, client):
        """Test creating a post without authentication."""
        post_data = {
            "title": "Unauthorized Post",
            "slug": "unauthorized-post",
            "content": "Content",
            "category_id": 1
        }

        response = await client.post("/api/v1/admin/posts/", json=post_data)
        assert response.status_code == 401

    async def test_create_post_as_admin(self, client, admin_headers, test_category):
        """Test creating a post as admin."""
        post_data = {
            "title": "Admin Created Post",
            "slug": "admin-created-post",
            "content": "This post was created by an admin",
            "category_id": test_category.id,
            "is_published": True
        }

        response = await client.post(
            "/api/v1/admin/posts/",
            json=post_data,
            headers=admin_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Admin Created Post"
        assert data["slug"] == "admin-created-post"