from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# Если есть, можно подключить метаданные моделей:
try:
    from app.storage.models import Base  # type: ignore
    target_metadata = Base.metadata
except Exception:
    target_metadata = None

# Логирование из alembic.ini
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# URL берём из переменной окружения Render
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise RuntimeError("DB_URL env var is required for alembic")

# --- async режим ---
def run_migrations_offline() -> None:
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = create_async_engine(DB_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
