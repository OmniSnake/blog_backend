"""Create posts and categories tables

Revision ID: 93d41156702f
Revises: 7b55a660e0b0
Create Date: 2025-09-25 22:55:47.443320

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func

# revision identifiers, used by Alembic.
revision = '93d41156702f'
down_revision = '7b55a660e0b0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_slug'), 'categories', ['slug'], unique=True)

    op.create_table('posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('excerpt', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_html', sa.Text(), nullable=False),
        sa.Column('is_published', sa.Boolean(), default=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_posts_id'), 'posts', ['id'], unique=False)
    op.create_index(op.f('ix_posts_slug'), 'posts', ['slug'], unique=True)

    categories_table = sa.sql.table('categories',
        sa.Column('name', sa.String),
        sa.Column('slug', sa.String),
        sa.Column('description', sa.Text)
    )

    op.bulk_insert(categories_table,
        [
            {'name': 'Technology', 'slug': 'technology', 'description': 'Articles about technology and programming'},
            {'name': 'Lifestyle', 'slug': 'lifestyle', 'description': 'Lifestyle and personal development'},
            {'name': 'Travel', 'slug': 'travel', 'description': 'Travel experiences and guides'},
        ]
    )


def downgrade() -> None:
    op.drop_table('posts')
    op.drop_table('categories')