"""add_ai_model_column_explicit

Revision ID: 82d5dcbe1d12
Revises: 96a8870b61ab
Create Date: 2024-11-12 03:45:15.801967

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82d5dcbe1d12'
down_revision: Union[str, None] = '96a8870b61ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
