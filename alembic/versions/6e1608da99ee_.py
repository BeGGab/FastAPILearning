"""empty message

Revision ID: 6e1608da99ee
Revises: 506970d493fd
Create Date: 2025-09-23 14:43:53.518527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e1608da99ee'
down_revision: Union[str, Sequence[str], None] = '506970d493fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
