# app/storage/models_extras.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, JSON, String, Integer, DateTime, func
from app.storage.db import Base  # твоя декларативная база

class CastingSession(Base):
    __tablename__ = "casting_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    started_at: Mapped[DateTime] = mapped_column(server_default=func.now())
    finished_at: Mapped[DateTime | None]
    answers: Mapped[dict] = mapped_column(JSON)
    result: Mapped[str | None] = mapped_column(String(64))
    source: Mapped[str | None] = mapped_column(String(64))

class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    casting_session_id: Mapped[int | None] = mapped_column(ForeignKey("casting_sessions.id"), nullable=True)
    emoji: Mapped[str] = mapped_column(String(8))
    phrase: Mapped[str | None] = mapped_column(String(140))
    created_at: Mapped[DateTime] = mapped_column(server_default=func.now())

class LeaderPath(Base):
    __tablename__ = "leader_paths"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    intent: Mapped[str] = mapped_column(String(32))
    micro_note: Mapped[str | None] = mapped_column(String(140))
    created_at: Mapped[DateTime] = mapped_column(server_default=func.now())
    source: Mapped[str | None] = mapped_column(String(64))

class PremiumRequest(Base):
    __tablename__ = "premium_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    text: Mapped[str] = mapped_column(String(280))
    status: Mapped[str] = mapped_column(String(16), default="new")  # new|seen|contacted
    created_at: Mapped[DateTime] = mapped_column(server_default=func.now())
    source: Mapped[str | None] = mapped_column(String(64))
