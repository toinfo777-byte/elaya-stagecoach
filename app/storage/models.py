# app/storage/models.py
from __future__ import annotations

import os
from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Integer, Boolean, Date, DateTime, BigInteger
from sqlalchemy.engine import make_url  # нормализация URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker, synonym

# ---- Render / файловое хранилище ----
# Для Render каталог /data доступен для записи между рестартами контейнера.
# Если DB_URL не задан, соберём его из DB_PATH (default: /data/bot.db).
DEFAULT_DB_PATH = "/data/bot.db"
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB_PATH)

# Гарантируем, что каталог существует (иначе SQLite упадёт "unable to open database file")
try:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
except Exception:
    pass

# Если указан DB_URL — используем его. Иначе строим из DB_PATH.
RAW_DB_URL = os.getenv("DB_URL") or f"sqlite+aiosqlite:///{DB_PATH}"

def _to_async_url(url: str) -> str:
    """Нормализуем строку подключения: усиливаем sync-драйверы на async-аналоги."""
    u = make_url(url)
    backend = u.get_backend_name()  # 'sqlite' | 'postgresql' | 'mysql' | ...
    driver = (u.drivername or "")
    # Уже async?
    if any(x in driver for x in ("+aiosqlite", "+asyncpg", "+aiomysql")):
        return str(u)
    if backend == "sqlite":
        return str(u.set(drivername="sqlite+aiosqlite"))
    if backend in ("postgresql", "postgres"):
        return str(u.set(drivername="postgresql+asyncpg"))
    if backend == "mysql":
        return str(u.set(drivername="mysql+aiomysql"))
    return str(u)

DB_URL = _to_async_url(RAW_DB_URL)

# На всякий случай — если это sqlite://, создадим директорию файла ещё раз,
# разобрав URL через make_url (важно для случаев с абсолютными путями).
try:
    parsed = make_url(DB_URL)
    if parsed.get_backend_name() == "sqlite" and parsed.database:
        db_dir = os.path.dirname(parsed.database)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
except Exception:
    pass

# ---- SQLAlchemy Base / Engine / Session ----
Base = declarative_base()

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
