"""add_ai_model_and_trial

Revision ID: ac5b8a1acfc8
Revises: your_revision_id
Create Date: 2024-11-12 00:50:08.260341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac5b8a1acfc8'
down_revision: Union[str, None] = 'your_revision_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
