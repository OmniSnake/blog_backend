import pytest
import pytest_asyncio
from app.repositories.post_repository import PostRepository


class TestPostRepository:
    @pytest_asyncio.fixture
    async def post_repo(self, session):
        return PostRepository(session)

    @pytest_asyncio.fixture
    async def test_post_data(self, post_repo, session, test_user, test_category):
        post_data = {
            "title": "Test Post",
            "slug": "test-post",
            "content": "Test content",
            "category_id": test_category.id,
            "author_id": test_user.id,
            "is_published": True
        }
        post = await post_repo.create(**post_data)
        await session.commit()
        return post

    async def test_create_post(self, post_repo, session, test_user, test_category):
        """Test creating a post."""
        post_data = {
            "title": "New Post",
            "slug": "new-post",
            "content": "New content",
            "category_id": test_category.id,
            "author_id": test_user.id
        }

        post = await post_repo.create(**post_data)
        await session.commit()

        assert post is not None
        assert post.title == "New Post"
        assert post.slug == "new-post"

    async def test_get_by_id(self, post_repo, test_post_data):
        """Test getting post by ID."""
        post = await post_repo.get_by_id(test_post_data.id)
        assert post is not None
        assert post.title == test_post_data.title

    async def test_get_by_slug(self, post_repo, test_post_data):
        """Test getting post by slug."""
        post = await post_repo.get_by_slug("test-post")
        assert post is not None
        assert post.id == test_post_data.id

    async def test_get_published_posts(self, post_repo, test_post_data):
        """Test getting published posts."""
        posts = await post_repo.get_published_posts()
        assert len(posts) > 0
        assert posts[0].is_published is True

    async def test_get_posts_by_category(self, post_repo, test_post_data, test_category):
        """Test getting posts by category."""
        posts = await post_repo.get_posts_by_category(test_category.slug)
        assert len(posts) > 0
        assert posts[0].category_id == test_category.id