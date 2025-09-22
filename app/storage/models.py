# app/storage/models.py
from __future__ import annotations

import os
from datetime import datetime, date
from typing import Optional

from sqlalchemy.orm import declarative_base, Mapped, mapped_column, synonym
from sqlalchemy import String, Integer, Boolean, Date, DateTime, BigInteger
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url  # для нормализации URL

# ---- Base ----
Base = declarative_base()

# ---- ENGINE & SESSIONMAKER (экспортируются) ----
RAW_DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:////data/db.sqlite")

def _to_async_url(url: str) -> str:
    """Нормализуем строку подключения: добавляем async-драйверы."""
    u = make_url(url)
    backend = u.get_backend_name()  # 'sqlite' | 'postgresql' | ...
    driver = (u.drivername or "")
    # Уже async?
    if any(x in driver for x in ["+aiosqlite", "+asyncpg", "+aiomysql"]):
        return str(u)

    if backend == "sqlite":
        return str(u.set(drivername="sqlite+aiosqlite"))
    if backend in ("postgresql", "postgres"):
        return str(u.set(drivername="postgresql+asyncpg"))
    if backend == "mysql":
        return str(u.set(drivername="mysql+aiomysql"))
    return str(u)

DB_URL = _to_async_url(RAW_DB_URL)

engine: AsyncEngine = create_async_engine(DB_URL, echo=False, future=True)
async_session_maker = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# ---- МОДЕЛИ ----

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TrainingLog(Base):
    __tablename__ = "training_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # базовый контракт
    tg_id: Mapped[int] = mapped_column(BigInteger, index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    level: Mapped[str] = mapped_column(String(16))   # 'beginner' | 'medium' | 'pro'
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # ✅ совместимость со старым кодом:
    #   - repo.py использует user_id и day
    user_id = synonym("tg_id")
    day = synonym("date")


class CastingForm(Base):
    __tablename__ = "casting_forms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, index=True)
    name: Mapped[str] = mapped_column(String(128))
    age: Mapped[int] = mapped_column(Integer)
    city: Mapped[str] = mapped_column(String(64))
    experience: Mapped[str] = mapped_column(String(32))
    contact: Mapped[str] = mapped_column(String(128))
    portfolio: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    agree_contact: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


__all__ = [
    "Base",
    "engine",
    "async_session_maker",
    "Profile",
    "TrainingLog",
    "CastingForm",
]
