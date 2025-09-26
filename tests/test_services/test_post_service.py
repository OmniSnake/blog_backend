import pytest
import pytest_asyncio
from app.services.post_service import PostService
from app.schemas.post import PostCreate, PostUpdate


class TestPostService:
    @pytest_asyncio.fixture
    async def post_service(self, session):
        from app.repositories.post_repository import PostRepository
        from app.repositories.category_repository import CategoryRepository

        post_repo = PostRepository(session)
        category_repo = CategoryRepository(session)

        return PostService(post_repo, category_repo, session)

    async def test_create_post_success(self, post_service, test_user, test_category):
        """Test successful post creation."""
        post_data = PostCreate(
            title="Test Post",
            slug="test-post",
            content="This is test content for the post",
            category_id=test_category.id,
            is_published=True
        )

        success, error = await post_service.create_post(test_user.id, post_data)
        assert success is True
        assert error is None

    async def test_create_post_invalid_category(self, post_service, test_user):
        """Test post creation with invalid category."""
        post_data = PostCreate(
            title="Test Post",
            slug="test-post",
            content="Test content",
            category_id=999,
            is_published=True
        )

        success, error = await post_service.create_post(test_user.id, post_data)
        assert success is False
        assert "Category not found" in error

    async def test_create_post_duplicate_slug(self, post_service, test_user, test_category):
        """Test post creation with duplicate slug."""
        post_data1 = PostCreate(
            title="First Post",
            slug="duplicate-slug",
            content="First post content",
            category_id=test_category.id
        )
        success1, error1 = await post_service.create_post(test_user.id, post_data1)
        assert success1 is True

        post_data2 = PostCreate(
            title="Second Post",
            slug="duplicate-slug",
            content="Second post content",
            category_id=test_category.id
        )
        success2, error2 = await post_service.create_post(test_user.id, post_data2)
        assert success2 is False
        assert "already exists" in error2

    async def test_update_post_success(self, post_service, test_user, test_category, session):
        """Test successful post update."""
        from app.repositories.post_repository import PostRepository

        post_repo = PostRepository(session)
        post = await post_repo.create(
            title="Original Title",
            slug="original-slug",
            content="Original content",
            category_id=test_category.id,
            author_id=test_user.id
        )
        await session.commit()

        update_data = PostUpdate(
            title="Updated Title",
            content="Updated content"
        )

        success, error = await post_service.update_post(post.id, update_data)
        assert success is True
        assert error is None

        updated_post = await post_repo.get_by_id(post.id)
        assert updated_post.title == "Updated Title"
        assert updated_post.content == "Updated content"

    async def test_delete_post_success(self, post_service, test_user, test_category, session):
        """Test successful post deletion."""
        from app.repositories.post_repository import PostRepository

        post_repo = PostRepository(session)
        post = await post_repo.create(
            title="Post to delete",
            slug="delete-me",
            content="Content",
            category_id=test_category.id,
            author_id=test_user.id
        )
        await session.commit()

        success, error = await post_service.delete_post(post.id)
        assert success is True
        assert error is None

        deleted_post = await post_repo.get_by_id(post.id)
        assert deleted_post.is_active is False