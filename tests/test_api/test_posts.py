import pytest


class TestPostsAPI:
    def test_get_posts_public(self, client, test_category, test_user, session):
        """Test getting public posts."""
        from app.repositories.post_repository import PostRepository
        import asyncio

        async def create_test_post():
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

        asyncio.run(create_test_post())

        response = client.get("/api/v1/posts/")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert len(data["posts"]) > 0

    def test_get_post_by_slug_public(self, client, test_category, test_user, session):
        """Test getting a specific post by slug."""
        from app.repositories.post_repository import PostRepository
        import asyncio

        async def create_test_post():
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

        asyncio.run(create_test_post())

        response = client.get("/api/v1/posts/specific-post")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "specific-post"
        assert data["title"] == "Specific Post"

    def test_get_post_not_found(self, client):
        """Test getting a non-existent post."""
        response = client.get("/api/v1/posts/non-existent-slug")
        assert response.status_code == 404

    def test_create_post_unauthorized(self, client):
        """Test creating a post without authentication."""
        post_data = {
            "title": "Unauthorized Post",
            "slug": "unauthorized-post",
            "content": "Content",
            "category_id": 1
        }

        response = client.post("/api/v1/admin/posts/", json=post_data)
        assert response.status_code == 403

    def test_create_post_as_admin(self, client, admin_headers, test_category):
        """Test creating a post as admin."""
        post_data = {
            "title": "Admin Created Post",
            "slug": "admin-created-post",
            "content": "This post was created by an admin",
            "category_id": test_category.id,
            "is_published": True
        }

        response = client.post(
            "/api/v1/admin/posts/",
            json=post_data,
            headers=admin_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Admin Created Post"
        assert data["slug"] == "admin-created-post"

    def test_update_post_as_admin(self, client, admin_headers, test_category, test_user, session):
        """Test updating a post as admin."""
        from app.repositories.post_repository import PostRepository
        import asyncio

        async def create_test_post():
            post_repo = PostRepository(session)
            post = await post_repo.create(
                title="Original Post",
                slug="original-post",
                content="Original content",
                category_id=test_category.id,
                author_id=test_user.id,
                is_published=True
            )
            await session.commit()
            return post.id

        post_id = asyncio.run(create_test_post())

        update_data = {
            "title": "Updated Post",
            "slug": "updated-post",
            "content": "Updated content",
            "category_id": test_category.id,
            "is_published": False
        }

        response = client.put(
            f"/api/v1/admin/posts/{post_id}",
            json=update_data,
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Post"
        assert data["slug"] == "updated-post"

    def test_delete_post_as_admin(self, client, admin_headers, test_category, test_user, session):
        """Test deleting a post as admin."""
        from app.repositories.post_repository import PostRepository
        import asyncio

        async def create_test_post():
            post_repo = PostRepository(session)
            post = await post_repo.create(
                title="Post to Delete",
                slug="post-to-delete",
                content="Content to delete",
                category_id=test_category.id,
                author_id=test_user.id,
                is_published=True
            )
            await session.commit()
            return post.id

        post_id = asyncio.run(create_test_post())

        response = client.delete(
            f"/api/v1/admin/posts/{post_id}",
            headers=admin_headers
        )
        assert response.status_code == 204

        response = client.get("/api/v1/posts/post-to-delete")
        assert response.status_code == 404