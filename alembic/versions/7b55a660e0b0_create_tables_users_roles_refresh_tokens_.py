"""Create tables: users, roles, refresh_tokens, user_roles

Revision ID: 7b55a660e0b0
Revises: b5df4cac4c5c
Create Date: 2025-09-25 18:03:08.574004

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

revision = '7b55a660e0b0'
down_revision = 'b5df4cac4c5c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('permissions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)

    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    op.create_table('user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    op.create_table('refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=512), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_token'), 'refresh_tokens', ['token'], unique=True)

    roles_table = sa.sql.table('roles',
        sa.Column('name', sa.String),
        sa.Column('description', sa.Text),
        sa.Column('permissions', sa.Text)
    )

    op.bulk_insert(roles_table,
        [
            {
                'name': 'admin',
                'description': 'Administrator',
                'permissions': '["post:create", "post:read", "post:update", "post:delete", "category:create", "category:read", "category:update", "category:delete", "user:read", "user:update", "user:delete", "admin:read", "admin:update", "admin:delete"]'
            },
            {
                'name': 'user',
                'description': 'Regular user',
                'permissions': '["post:read", "category:read"]'
            }
        ]
    )


def downgrade() -> None:
    op.drop_table('refresh_tokens')
    op.drop_table('user_roles')
    op.drop_table('users')
    op.drop_table('roles')