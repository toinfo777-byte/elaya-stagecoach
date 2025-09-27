# app/storage/db.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

def _dsn() -> str:
    # По умолчанию SQLite локально; на проде укажи DATABASE_URL через env
    url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data.db")
    # Render/Heroku иногда дают postgres:// — приводим к asyncpg
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url

DATABASE_URL = _dsn()

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    future=True,
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autoflush=False,
)

class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс моделей (используется models_extras и т.п.)."""
    pass
