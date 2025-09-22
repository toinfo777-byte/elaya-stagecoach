# migrations/env.py
from __future__ import annotations
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

# 1) ЛОГИ
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2) ИМПОРТ БАЗЫ И МОДЕЛЕЙ
from app.storage.db import DATABASE_URL, Base  # <- из нашего mini-модуля БД
import app.storage.models_extras               # <- ВАЖНО: чтобы модели зарегистрировались

target_metadata = Base.metadata

# 3) OFFLINE (генерация SQL без коннекта)
def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        render_as_batch=True,   # полезно для SQLite
    )
    with context.begin_transaction():
        context.run_migrations()

# 4) ONLINE (c async-движком)
def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    engine = create_async_engine(DATABASE_URL, poolclass=NullPool, future=True)
    async with engine.connect() as conn:
        await conn.run_sync(do_run_migrations)
    await engine.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
