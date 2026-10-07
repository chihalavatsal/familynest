"""add employment enrichment and death place

Revision ID: a1b2c3d4e5f6
Revises: f08bf48bbcf3
Create Date: 2026-10-01 17:46:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f08bf48bbcf3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # add columns to employments
    op.add_column('employments', sa.Column('department', sa.String(length=255), nullable=True))
    op.add_column('employments', sa.Column('location', sa.String(length=255), nullable=True))
    op.add_column('employments', sa.Column('employment_type', sa.String(length=50), nullable=True))
    op.add_column('employments', sa.Column('description', sa.Text(), nullable=True))
    
    # add column to people
    op.add_column('people', sa.Column('death_place', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # drop columns from people
    op.drop_column('people', 'death_place')
    
    # drop columns from employments
    op.drop_column('employments', 'description')
    op.drop_column('employments', 'employment_type')
    op.drop_column('employments', 'location')
    op.drop_column('employments', 'department')
