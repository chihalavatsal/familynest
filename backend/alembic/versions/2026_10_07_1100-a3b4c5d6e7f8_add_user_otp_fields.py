"""add user otp fields

Revision ID: a3b4c5d6e7f8
Revises: a1b2c3d4e5f6
Create Date: 2026-10-07 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3b4c5d6e7f8'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('otp_code', sa.String(length=10), nullable=True))
    op.add_column('users', sa.Column('otp_expires_at', sa.TIMESTAMP(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'otp_expires_at')
    op.drop_column('users', 'otp_code')
