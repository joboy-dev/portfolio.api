"""add content columns to blogs table

Revision ID: adb00f3d86c6
Revises: 04284b2f1795
Create Date: 2026-06-23 23:35:42.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'adb00f3d86c6'
down_revision: Union[str, None] = '04284b2f1795'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('blogs', sa.Column('title', sa.String(), nullable=False, server_default=''))
    op.add_column('blogs', sa.Column('slug', sa.String(), nullable=False, server_default=''))
    op.add_column('blogs', sa.Column('excerpt', sa.Text(), nullable=True))
    op.add_column('blogs', sa.Column('content', sa.Text(), nullable=False, server_default=''))
    op.add_column('blogs', sa.Column('cover_image_url', sa.String(), nullable=True))
    op.add_column('blogs', sa.Column('is_published', sa.Boolean(), server_default='false'))
    op.add_column('blogs', sa.Column('published_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_blogs_slug'), 'blogs', ['slug'], unique=True)
    op.alter_column('blogs', 'title', server_default=None)
    op.alter_column('blogs', 'slug', server_default=None)
    op.alter_column('blogs', 'content', server_default=None)


def downgrade() -> None:
    op.drop_index(op.f('ix_blogs_slug'), table_name='blogs')
    op.drop_column('blogs', 'published_at')
    op.drop_column('blogs', 'is_published')
    op.drop_column('blogs', 'cover_image_url')
    op.drop_column('blogs', 'content')
    op.drop_column('blogs', 'excerpt')
    op.drop_column('blogs', 'slug')
    op.drop_column('blogs', 'title')
