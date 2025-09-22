# app/storage/models.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, Boolean

# === Базовый класс ===
class Base(DeclarativeBase):
    ...


# --- Пользователь ---
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(255))
    tz: Mapped[str | None] = mapped_column(String(64))
    goal: Mapped[str | None] = mapped_column(String(255))
    exp_level: Mapped[int | None] = mapped_column(Integer)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime)
    consent_at: Mapped[datetime | None] = mapped_column(DateTime)

    source: Mapped[str | None] = mapped_column(String(64), nullable=True)

    drill_runs: Mapped[list["DrillRun"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    leads: Mapped[list["Lead"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    events: Mapped[list["Event"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    test_results: Mapped[list["TestResult"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    feedbacks: Mapped[list["Feedback"]] = relationship(back_populates="user", cascade="all, delete-orphan")


# --- Этюд и прохождения ---
class Drill(Base):
    __tablename__ = "drills"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)


class DrillRun(Base):
    __tablename__ = "drill_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    drill_id: Mapped[str] = mapped_column(ForeignKey("drills.id", ondelete="CASCADE"))
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    result_json: Mapped[dict] = mapped_column(JSON, default=dict)
    success_bool: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="drill_runs")
    drill: Mapped["Drill"] = relationship()


# --- Мини-кастинг ---
class Test(Base):
    __tablename__ = "tests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)


class TestResult(Base):
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    axes_json: Mapped[dict] = mapped_column(JSON, default=dict)
    score_total: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="test_results")


# --- События ---
class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(64))
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="events")


# --- Лиды ---
class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    channel: Mapped[str] = mapped_column(String(32))
    contact: Mapped[str] = mapped_column(String(255))
    note: Mapped[str | None] = mapped_column(String(500), default=None)
    track: Mapped[str | None] = mapped_column(String(32), default=None)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="leads")


# --- Обратная связь ---
class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    first_source: Mapped[str | None] = mapped_column(String(64), default=None)
    context: Mapped[str] = mapped_column(String(32))
    context_id: Mapped[str | None] = mapped_column(String(64), default=None)
    score: Mapped[int | None] = mapped_column(Integer, default=None)
    text: Mapped[str | None] = mapped_column(String(2000), default=None)
    voice_file_id: Mapped[str | None] = mapped_column(String(256), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="feedbacks")


# --- Заявки на Расширенную версию ---
class PremiumRequest(Base):
    __tablename__ = "premium_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    tg_username: Mapped[str | None] = mapped_column(String(255), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(32), default="new")
    meta: Mapped[dict] = mapped_column(JSON, default=dict)


# --- Асинхронный движок и фабрика сессий ---
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine.url import make_url
from app.config import settings

def _make_async_dsn(dsn: str) -> str:
    url = make_url(dsn)
    drv = url.drivername
    if "+" not in drv:
        if drv in ("sqlite",):
            drv = "sqlite+aiosqlite"
        elif drv in ("postgresql", "postgres"):
            drv = "postgresql+asyncpg"
    return str(url.set(drivername=drv))

ASYNC_DB_URL = _make_async_dsn(settings.db_url)
engine = create_async_engine(ASYNC_DB_URL, pool_pre_ping=True, future=True)
async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

__all__ = [
    "Base",
    "engine",
    "async_session_maker",
    "User", "Drill", "DrillRun", "Test", "TestResult",
    "Event", "Lead", "Feedback", "PremiumRequest",
]
