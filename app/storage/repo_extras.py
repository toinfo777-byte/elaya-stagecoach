from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy import insert, update, select
from app.storage.db import async_session
from app.storage.models_extras import CastingSession, Feedback, LeaderPath, PremiumRequest

# ─────────────────────────────────────────────────────────────────────────────
# КАСТИНГ / ФИДБЭК / ЛИДЕР / ПРЕМИУМ
# ─────────────────────────────────────────────────────────────────────────────

async def save_casting_session(user_id: int, answers: list, result: str) -> None:
    async with async_session() as s:
        await s.execute(
            insert(CastingSession).values(
                user_id=user_id,
                answers=answers,
                result=result,
                finished_at=datetime.utcnow(),
                source="mini",
            )
        )
        await s.commit()


async def save_feedback(user_id: int, emoji: Optional[str], phrase: Optional[str]) -> None:
    async with async_session() as s:
        await s.execute(
            insert(Feedback).values(
                user_id=user_id,
                emoji=emoji,
                phrase=phrase,
                created_at=datetime.utcnow(),
            )
        )
        await s.commit()


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
                .values(intent=intent, micro_note=micro_note, updated_at=datetime.utcnow())
            )
        else:
            await s.execute(
                insert(LeaderPath).values(
                    user_id=user_id,
                    intent=intent,
                    micro_note=micro_note,
                    source="leader",
                    created_at=datetime.utcnow(),
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
                created_at=datetime.utcnow(),
            )
        )
        await s.commit()


# ─────────────────────────────────────────────────────────────────────────────
# ТРЕНИРОВКИ (безопасные заглушки: если модели нет — молча пропускаем)
# ─────────────────────────────────────────────────────────────────────────────

async def save_training_episode(user_id: int, level: str) -> None:
    """
    Пишем факт выполнения тренировки. Если модель TrainingEpisode отсутствует —
    молча пропускаем (чтобы бот не падал).
    """
    try:
        from app.storage.models_extras import TrainingEpisode  # type: ignore
    except Exception:
        return

    async with async_session() as s:
        await s.execute(
            insert(TrainingEpisode).values(
                user_id=user_id,
                level=str(level),
                created_at=datetime.utcnow(),
            )
        )
        await s.commit()


async def get_progress(user_id: int) -> Tuple[int, int]:
    """
    Возвращает (streak, last7). Если модели нет — (0, 0).
    streak — количество подряд идущих дней (включая сегодня при наличии события).
    last7 — количество тренировочных эпизодов за последние 7 дней.
    """
    try:
        from app.storage.models_extras import TrainingEpisode  # type: ignore
    except Exception:
        return (0, 0)

    now = datetime.utcnow()
    since_7 = now - timedelta(days=7)
    since_30 = now - timedelta(days=30)

    async with async_session() as s:
        # последние 7 дней — просто считаем эпизоды
        q7 = select(TrainingEpisode.created_at).where(
            TrainingEpisode.user_id == user_id,
            TrainingEpisode.created_at >= since_7,
        )
        res7 = (await s.execute(q7)).scalars().all()
        last7 = len(res7)

        # для стрика возьмём до 30 дней и посчитаем уникальные даты
        q30 = select(TrainingEpisode.created_at).where(
            TrainingEpisode.user_id == user_id,
            TrainingEpisode.created_at >= since_30,
        )
        res30 = (await s.execute(q30)).scalars().all()

    # приводим к датам (UTC)
    days = {dt.date() for dt in res30}
    if not days:
        return (0, last7)

    # считаем сколько дней подряд, начиная с сегодня
    streak = 0
    cur = now.date()
    while cur in days:
        streak += 1
        cur = cur - timedelta(days=1)

    return (streak, last7)


__all__ = [
    "save_casting_session",
    "save_feedback",
    "save_leader_intent",
    "save_premium_request",
    "save_training_episode",
    "get_progress",
]
