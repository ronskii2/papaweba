"""add_ai_model_to_users

Revision ID: 8dca15b4686a
Revises: ac5b8a1acfc8
Create Date: 2024-11-12 03:24:15.988282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8dca15b4686a'
down_revision: Union[str, None] = 'ac5b8a1acfc8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
