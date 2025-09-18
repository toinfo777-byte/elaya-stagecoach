"""add notify fields + premium_requests table

Revision ID: 20250918_add_premium
Revises: 
Create Date: 2025-09-18

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20250918_add_premium"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    is_sqlite = dialect == "sqlite"

    # --- users: уведомления по умолчанию ---
    # Boolean default: sqlite -> 0/1, postgres -> false/true
    bool_default = sa.text("0") if is_sqlite else sa.text("false")

    op.add_column(
        "users",
        sa.Column("notify_enabled", sa.Boolean(), nullable=False, server_default=bool_default),
    )
    op.add_column(
        "users",
        sa.Column("notify_hour", sa.SmallInteger(), nullable=False, server_default=sa.text("9")),
    )

    # --- premium_requests: json/meta и дефолты под каждую БД ---
    json_type = sa.Text() if is_sqlite else sa.JSON()
    meta_default = sa.text("'{}'") if is_sqlite else sa.text("'{}'::jsonb")

    op.create_table(
        "premium_requests",
        sa.Column("id", sa.BigInteger(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("tg_username", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'new'")),
        sa.Column("meta", json_type, nullable=False, server_default=meta_default),
    )

    op.create_index("idx_premium_requests_user_id", "premium_requests", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_premium_requests_user_id", table_name="premium_requests")
    op.drop_table("premium_requests")

    op.drop_column("users", "notify_hour")
    op.drop_column("users", "notify_enabled")
