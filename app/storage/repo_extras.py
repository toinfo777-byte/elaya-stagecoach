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

# --- Мини-кастинг ------------------------------------------------------------

async def save_casting_session(user_id: int, answers: list, result: str) -> None:
    """Сохраняем итог мини-кастинга (ответы + простой результат)."""
    async with async_session() as s:
        await s.execute(
            insert(CastingSession).values(
                user_id=user_id,
                answers=answers,
                result=result,
                finished_at=datetime.utcnow(),  # naive-UTC в проекте
                source="mini",
            )
        )
        await s.commit()


async def save_feedback(user_id: int, emoji: str, phrase: str | None) -> None:
    """Сохраняем быстрый отзыв (эмодзи + опциональное слово)."""
    async with async_session() as s:
        await s.execute(
            insert(Feedback).values(
                user_id=user_id,
                emoji=emoji,
                phrase=phrase,
            )
        )
        await s.commit()


# --- Путь лидера -------------------------------------------------------------

async def save_leader_intent(
    user_id: int,
    intent: str,
    micro_note: str | None,
    upsert: bool = False,
) -> None:
    """Сохраняем/обновляем намерение и микро-заметку в «Пути лидера»."""
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
    """Сохраняем короткую заявку в «Расширенную версию»."""
    async with async_session() as s:
        await s.execute(
            insert(PremiumRequest).values(
                user_id=user_id,
                text=text,
                source=source,
            )
        )
        await s.commit()


# --- Прогресс / события ------------------------------------------------------

async def log_progress_event(
    user_id: int,
    kind: str,  # например: "training" | "minicasting" | "leader_path"
    meta: Optional[dict[str, Any]] = None,
    at: Optional[datetime] = None,
) -> None:
    """
    Минимальная реализация: пишет событие в лог.
    Замените на запись в БД, когда будет готова таблица.
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
    except Exception:
        logger.exception("Failed to log progress event")


async def get_progress(user_id: int) -> dict[str, int]:
    """
    Заглушка для раздела «📈 Мой прогресс».
    Вернёт нули, чтобы бот не падал на импорте.
    При необходимости перепишите на реальный расчёт из БД.
    """
    logger.info("get_progress(user_id=%s) -> stub zeros", user_id)
    return {"streak": 0, "episodes_7d": 0}


__all__ = [
    "save_casting_session",
    "save_feedback",
    "save_leader_intent",
    "save_premium_request",
    "log_progress_event",
    "get_progress",
]
