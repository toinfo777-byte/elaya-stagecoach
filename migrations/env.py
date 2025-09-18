# migrations/env.py
from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig
from typing import Optional

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# --- алембиковский конфиг и логирование ---------------------------------------
config = context.config  # type: ignore[attr-defined]
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- metadata проекта ----------------------------------------------------------
# Импортируй metadata своих моделей.
# Если другой путь/имя — поправь импорт ниже.
try:
    from app.storage.models import Base  # type: ignore
    target_metadata = Base.metadata
except Exception:
    target_metadata = None  # миграции будут только по raw SQL, если что

# --- URL к БД: берём из ENV или из alembic.ini и нормализуем к async -----------
DB_URL: Optional[str] = os.getenv("DB_URL") or config.get_main_option("sqlalchemy.url")

if not DB_URL:
    raise RuntimeError(
        "DB_URL is not set (neither env nor alembic.ini). "
        "Set ENV VAR DB_URL or sqlalchemy.url in alembic.ini"
    )

# нормализуем под async-драйвер
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DB_URL.startswith("postgresql://") and "+asyncpg" not in DB_URL:
    DB_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


# --- offline режим -------------------------------------------------------------
def run_migrations_offline() -> None:
    """
    Запуск миграций без соединения (генерация SQL).
    """
    url = DB_URL
    assert url is not None
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# --- online режим --------------------------------------------------------------
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
    assert DB_URL is not None
    connectable: AsyncEngine = create_async_engine(DB_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# --- точка входа ---------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
