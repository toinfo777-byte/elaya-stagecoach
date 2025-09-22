# app/storage/models_extras.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, JSON, String, Integer, DateTime, func

from app.storage.db import Base


class CastingSession(Base):
    __tablename__ = "casting_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)

    # ⬇️ В аннотации — python datetime, а тип столбца задаём в mapped_column
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    answers: Mapped[Dict[str, Any]] = mapped_column(JSON)
    result: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    casting_session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("casting_sessions.id"), nullable=True)

    emoji: Mapped[str] = mapped_column(String(8))
    phrase: Mapped[Optional[str]] = mapped_column(String(140), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LeaderPath(Base):
    __tablename__ = "leader_paths"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    intent: Mapped[str] = mapped_column(String(32))
    micro_note: Mapped[Optional[str]] = mapped_column(String(140), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    source: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class PremiumRequest(Base):
    __tablename__ = "premium_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(String(280))
    status: Mapped[str] = mapped_column(String(16), default="new")  # new|seen|contacted
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    source: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
