# app/storage/repo_extras.py
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any, Optional

from sqlalchemy import insert, update

from app.storage.db import async_session
from app.storage.models_extras import (
    CastingSession,
    Feedback,
    LeaderPath,
    PremiumRequest,
)

logger = logging.getLogger(__name__)

# --- Мини-кастинг: сессия и отзыв --------------------------------------------

async def save_casting_session(user_id: int, answers: list, result: str) -> None:
    """
    Сохраняем итог мини-кастинга (набор ответов + простой результат).
    """
    async with async_session() as s:
        await s.execute(
            insert(CastingSession).values(
                user_id=user_id,
                answers=answers,
                result=result,
                finished_at=datetime.utcnow(),  # придерживаемся вашего naive-UTC
                source="mini",
            )
        )
        await s.commit()


async def save_feedback(user_id: int, emoji: str, phrase: str | None) -> None:
    """
    Сохраняем быстрый отзыв пользователя (эмодзи + опциональное слово).
    """
    async with async_session() as s:
        await s.execute(
            insert(Feedback).values(
                user_id=user_id,
                emoji=emoji,
                phrase=phrase,
            )
        )
        await s.commit()


# --- Путь лидера --------------------------------------------------------------

async def save_leader_intent(
    user_id: int,
    intent: str,
    micro_note: str | None,
    upsert: bool = False,
) -> None:
    """
    Сохраняем намерение пользователя в «Пути лидера».
    Если upsert=True — обновляем запись по user_id.
    """
    async with async_session() as s:
        if upsert:
            await s.execute(
                update(LeaderPath)
                .where(LeaderPath.user_id == user_id)
                .values(intent=intent, micro_note=micro_note)
            )
        else:
            await s.execute(
                insert(LeaderPath).values(
                    user_id=user_id,
                    intent=intent,
                    micro_note=micro_note,
                    source="leader",
                )
            )
        await s.commit()


async def save_premium_request(user_id: int, text: str, source: str) -> None:
    """
    Сохраняем короткую заявку пользователя в «Расширенную версию».
    """
    async with async_session() as s:
        await s.execute(
            insert(PremiumRequest).values(
                user_id=user_id,
                text=text,
                source=source,
            )
        )
        await s.commit()


# --- Прогресс / события (заглушка, чтобы не падать) --------------------------

async def log_progress_event(
    user_id: int,
    kind: str,  # например: "training" | "minicasting" | "leader_path"
    meta: Optional[dict[str, Any]] = None,
    at: Optional[datetime] = None,
) -> None:
    """
    Минимальная реализация, чтобы модуль не падал при импорте.

    Сейчас просто пишет событие в лог. Когда будете готовы —
    замените тело на запись в БД (например, в таблицу progress_events).
    """
    at = at or datetime.utcnow()
    try:
        logger.info(
            "[progress] user=%s kind=%s at=%s meta=%s",
            user_id,
            kind,
            at.isoformat(),
            meta,
        )
        # Пример будущей реализации:
        # async with async_session() as s:
        #     await s.execute(insert(ProgressEvent).values(
        #         user_id=user_id, kind=kind, created_at=at, meta=meta or {}
        #     ))
        #     await s.commit()
    except Exception:
        # даже если логирование упадёт — не роняем обработчик
        logger.exception("Failed to log progress event")


__all__ = [
    "save_casting_session",
    "save_feedback",
    "save_leader_intent",
    "save_premium_request",
    "log_progress_event",
]
