from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, BigInteger, String, DateTime, JSON, func

# Base берём из мини-модуля БД
from app.storage.db import Base


# === 🎭 Мини-кастинг =========================================================

class CastingSession(Base):
    __tablename__ = "casting_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)

    # ответы анкеты (Да/Нет/Пауза/Тембр/…)
    answers: Mapped[list | None] = mapped_column(JSON, default=list)

    # агрегированный результат: 'ok' | 'pause' | 'tempo' | …
    result: Mapped[str] = mapped_column(String(32), nullable=False)

    # источник: 'mini' и т.п.
    source: Mapped[str | None] = mapped_column(String(32))

    # когда закончили мини-кастинг
    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)

    emoji: Mapped[str | None] = mapped_column(String(10))
    phrase: Mapped[str | None] = mapped_column(String(280))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# === 🧭 Путь лидера ==========================================================

class LeaderPath(Base):
    __tablename__ = "leader_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)

    intent: Mapped[str] = mapped_column(String(32), nullable=False)          # voice|public|stage|other
    micro_note: Mapped[str | None] = mapped_column(String(140))
    source: Mapped[str | None] = mapped_column(String(32))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PremiumRequest(Base):
    __tablename__ = "premium_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)

    # intent оставил опциональным — твой save_premium_request его не передаёт
    intent: Mapped[str | None] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(String(512))
    source: Mapped[str | None] = mapped_column(String(32))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# === 📈 Прогресс / события ====================================================

class ProgressEvent(Base):
    __tablename__ = "progress_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)

    # 'training' | 'minicasting'
    kind: Mapped[str] = mapped_column(String(32), nullable=False)

    # для training: 'l1'|'l2'|'l3'; для прочих — None
    level: Mapped[str | None] = mapped_column(String(16))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
