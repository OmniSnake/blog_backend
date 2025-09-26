import pytest
from app.models.post import Post


class TestPostModel:
    def test_post_creation(self):
        """Test post model creation."""
        post = Post(
            title="Test Post",
            slug="test-post",
            content="Test content",
            category_id=1,
            author_id=1,
            is_published=True,
            is_active=True,
        )

        assert post.title == "Test Post"
        assert post.slug == "test-post"
        assert post.content == "Test content"
        assert post.category_id == 1
        assert post.author_id == 1
        assert post.is_published is True
        assert post.is_active is True

    def test_post_repr(self):
        """Test post string representation."""
        post = Post(title="Test Post", slug="test", content="content", category_id=1, author_id=1)
        assert repr(post) == "<Post Test Post>"

    def test_sanitize_html(self):
        """Test HTML sanitization."""
        dirty_html = "<script>alert('xss')</script><p>Safe content</p>"
        clean_html = Post.sanitize_html(dirty_html)

        assert "script" not in clean_html
        assert "Safe content" in clean_html