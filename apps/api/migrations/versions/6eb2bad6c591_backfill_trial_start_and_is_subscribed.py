"""Backfill trial_start and is_subscribed

Revision ID: 6eb2bad6c591
Revises: 7cb1232c4c3d
Create Date: 2025-04-15 14:02:55.802850

"""

from datetime import datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6eb2bad6c591"
down_revision: Union[str, None] = "7cb1232c4c3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Backfill null trial_start and is_subscribed values."""
    users_table = sa.table(
        "users",
        sa.column("trial_start", sa.DateTime()),
        sa.column("is_subscribed", sa.Boolean()),
    )

    now = datetime.utcnow()

    op.execute(
        users_table.update()
        .where(users_table.c.trial_start == None)
        .values(trial_start=now)
    )

    op.execute(
        users_table.update()
        .where(users_table.c.is_subscribed == None)
        .values(is_subscribed=False)
    )


def downgrade() -> None:
    """Reset backfilled fields to null."""
    users_table = sa.table(
        "users",
        sa.column("trial_start", sa.DateTime()),
        sa.column("is_subscribed", sa.Boolean()),
    )

    op.execute(
        users_table.update()
        .where(users_table.c.trial_start != None)
        .values(trial_start=None)
    )

    op.execute(
        users_table.update()
        .where(users_table.c.is_subscribed == True)
        .values(is_subscribed=None)
    )
