"""add notify fields + premium_requests table

Revision ID: 20250918_add_premium
Revises: 
Create Date: 2025-09-18

"""
from alembic import op
import sqlalchemy as sa


# уникальный ID миграции (можешь поменять)
revision: str = "20250918_add_premium"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # === Добавляем новые колонки в users ===
    op.add_column(
        "users",
        sa.Column("notify_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column(
        "users",
        sa.Column("notify_hour", sa.SmallInteger(), nullable=False, server_default="9"),
    )

    # === Создаём таблицу premium_requests ===
    op.create_table(
        "premium_requests",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("tg_username", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("status", sa.Text(), server_default="new", nullable=False),
        sa.Column("meta", sa.JSON(), server_default=sa.text("'{}'::jsonb"), nullable=False),
    )

    op.create_index(
        "idx_premium_requests_user_id",
        "premium_requests",
        ["user_id"],
    )


def downgrade() -> None:
    # Откат миграции
    op.drop_index("idx_premium_requests_user_id", table_name="premium_requests")
    op.drop_table("premium_requests")
    op.drop_column("users", "notify_hour")
    op.drop_column("users", "notify_enabled")
