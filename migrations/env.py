# migrations/env.py
from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig
from typing import Optional

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# Alembic config & logging
config = context.config  # type: ignore[attr-defined]
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Project metadata (если у тебя Base в другом месте — поправь импорт)
try:
    from app.storage.models import Base  # type: ignore
    target_metadata = Base.metadata
except Exception:
    target_metadata = None

# --- DB URL: env первее, потом alembic.ini -----------------------------------
DB_URL: Optional[str] = os.getenv("DB_URL") or config.get_main_option("sqlalchemy.url")
if not DB_URL:
    raise RuntimeError(
        "DB_URL is not set (neither env nor alembic.ini). "
        "Set ENV VAR DB_URL or sqlalchemy.url in alembic.ini"
    )

def _to_async_url(url: str) -> str:
    # Postgres → asyncpg
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # SQLite оставляем sync — alembic + sqlite работают отлично синхронно
    return url

ASYNC_URL = _to_async_url(DB_URL)

# --- offline mode --------------------------------------------------------------
def run_migrations_offline() -> None:
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

# --- online helpers ------------------------------------------------------------
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    # Если это SQLite — идём синхронным движком
    if DB_URL.startswith("sqlite"):
        engine = create_engine(DB_URL, poolclass=pool.NullPool)
        try:
            with engine.connect() as connection:
                do_run_migrations(connection)
        finally:
            engine.dispose()
        return

    # Иначе (Postgres и пр.) — async
    connectable: AsyncEngine = create_async_engine(ASYNC_URL, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

# --- entrypoint ---------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
