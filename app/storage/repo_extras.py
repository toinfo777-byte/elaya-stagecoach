# app/storage/repo_extras.py
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import insert, update

from app.storage.db import async_session
from app.storage.models_extras import CastingSession, Feedback, LeaderPath, PremiumRequest

logger = logging.getLogger(__name__)


# ===== Мини-кастинг =====
async def save_casting_session(user_id: int, answers: list[str], result: str) -> None:
    async with async_session() as s:
        await s.execute(
            insert(CastingSession).values(
                user_id=user_id,
                answers=answers,
                result=result,
                finished_at=datetime.now(timezone.utc),
                source="mini",
            )
        )
        await s.commit()


async def save_feedback(user_id: int, emoji: str, phrase: Optional[str]) -> None:
    async with async_session() as s:
        await s.execute(
            insert(Feedback).values(
                user_id=user_id,
                emoji=emoji,
                phrase=phrase,
            )
        )
        await s.commit()


# ===== Путь лидера / премиум =====
async def save_leader_intent(
    user_id: int,
    intent: str,
    micro_note: Optional[str],
    upsert: bool = False,
) -> None:
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
    async with async_session() as s:
        await s.execute(
            insert(PremiumRequest).values(
                user_id=user_id,
                text=text,
                source=source,
            )
        )
        await s.commit()


# ===== Прогресс: события/агрегация =====
async def log_progress_event(
    user_id: int,
    kind: str,                      # 'training' | 'minicasting' | 'leader' etc.
    meta: Optional[dict[str, Any]] = None,
    at: Optional[datetime] = None,
) -> None:
    """
    Минимальная реализация: просто логируем. При желании замените на запись в отдельную таблицу.
    """
    at = at or datetime.now(timezone.utc)
    logger.info(
        "progress_event user=%s kind=%s at=%s meta=%s",
        user_id, kind, at.isoformat(), meta or {},
    )


async def get_progress(user_id: int) -> dict[str, int]:
    """
    Безопасная заглушка: если нет отдельной таблицы ProgressEvent, вернём 0/0.
    При желании посчитайте эпизоды за 7д из CastingSession/других таблиц.
    """
    try:
        # пример грубой оценки по мини-кастингу за последние 7 дней
        since = datetime.now(timezone.utc) - timedelta(days=6)
        episodes_7d = 0
        # Если хотите считать по кастингам — раскоммитьте и подгоните под вашу БД.
        # from sqlalchemy import select, func
        # from app.storage.db import async_session
        # from app.storage.models_extras import CastingSession
        # async with async_session() as s:
        #     q = select(func.count()).select_from(CastingSession).where(
        #         CastingSession.user_id == user_id,
        #         CastingSession.finished_at >= since,
        #     )
        #     episodes_7d = (await s.execute(q)).scalar_one()
        return {"streak": 0, "episodes_7d": int(episodes_7d)}
    except Exception:  # на всякий случай не валим бота
        logger.exception("get_progress failed; return zeros")
        return {"streak": 0, "episodes_7d": 0}


__all__ = [
    "save_casting_session",
    "save_feedback",
    "save_leader_intent",
    "save_premium_request",
    "log_progress_event",
    "get_progress",
]
