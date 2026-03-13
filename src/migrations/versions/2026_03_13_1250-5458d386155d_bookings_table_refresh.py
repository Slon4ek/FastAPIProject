"""bookings table refresh

Revision ID: 5458d386155d
Revises: a23dcc52eb9c
Create Date: 2026-03-13 12:50:35.414855

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "5458d386155d"
down_revision: Union[str, Sequence[str], None] = "a23dcc52eb9c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bookings", sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)
    )
    op.add_column(
        "bookings", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("bookings", "updated_at")
    op.drop_column("bookings", "created_at")
