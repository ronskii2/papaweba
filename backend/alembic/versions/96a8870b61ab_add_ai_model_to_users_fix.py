"""add_ai_model_to_users_fix

Revision ID: 96a8870b61ab
Revises: 8dca15b4686a
Create Date: 2024-11-12 03:35:02.364123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96a8870b61ab'
down_revision: Union[str, None] = '8dca15b4686a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
