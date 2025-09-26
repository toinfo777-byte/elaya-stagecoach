# app/storage/repo_extras.py
from __future__ import annotations
from datetime import datetime, timedelta, timezone, date

from sqlalchemy import insert, update, select, and_
from app.storage.db import async_session
from app.storage.models_extras import (
    CastingSession, Feedback, LeaderPath, PremiumRequest, ProgressEvent
)

# ---- мини-кастинг -----------------------------------------------------------
async def save_casting_session(user_id: int, answers: list, result: str):
    async with async_session() as s:
        await s.execute(insert(CastingSession).values(
            user_id=user_id,
            answers=answers,
            result=result,
            finished_at=datetime.now(timezone.utc),
            source="mini",
        ))
        await s.commit()

async def save_feedback(user_id: int, emoji: str | None, phrase: str | None):
    async with async_session() as s:
        await s.execute(insert(Feedback).values(
            user_id=user_id,
            emoji=emoji,
            phrase=phrase,
        ))
        await s.commit()

# ---- путь лидера ------------------------------------------------------------
async def save_leader_intent(user_id: int, intent: str, micro_note: str | None, upsert: bool = False):
    async with async_session() as s:
        if upsert:
            await s.execute(
                update(LeaderPath)
                .where(LeaderPath.user_id == user_id)
                .set(dict(intent=intent, micro_note=micro_note))
            )
        else:
            await s.execute(insert(LeaderPath).values(
                user_id=user_id, intent=intent, micro_note=micro_note, source="leader"
            ))
        await s.commit()

async def save_premium_request(user_id: int, text: str, source: str):
    async with async_session() as s:
        await s.execute(insert(PremiumRequest).values(
            user_id=user_id, text=text, source=source
        ))
        await s.commit()

# ---- ПРОГРЕСС / СТАТИСТИКА --------------------------------------------------

async def log_progress_event(user_id: int, kind: str, level: str | None = None) -> None:
    """
    Записать событие прогресса.
    kind: 'training' | 'minicasting'
    level: 'l1'|'l2'|'l3' (для training), иначе None
    """
    async with async_session() as s:
        await s.execute(insert(ProgressEvent).values(
            user_id=user_id,
            kind=kind,
            level=level,
            created_at=datetime.now(timezone.utc),
        ))
        await s.commit()

async def log_training_done(user_id: int, level: str | None) -> None:
    await log_progress_event(user_id=user_id, kind="training", level=level)

async def get_progress(user_id: int) -> tuple[int, int, datetime]:
    """
    Возвращает (streak, last7, updated_at)
    - streak: подряд идущие дни с сегодняшнего (UTC) с событиями kind='training'
    - last7: количество событий kind in ('training','minicasting') за 7 дней (UTC)
    """
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=60)

    async with async_session() as s:
        res = await s.execute(
            select(ProgressEvent.kind, ProgressEvent.created_at)
            .where(
                and_(
                    ProgressEvent.user_id == user_id,
                    ProgressEvent.created_at >= since,
                )
            )
            .order_by(ProgressEvent.created_at.desc())
        )
        rows = res.all()

    # last7
    last7_cut = now - timedelta(days=7)
    last7 = sum(1 for kind, ts in rows if ts >= last7_cut and kind in ("training", "minicasting"))

    # streak по дням (UTC)
    training_days: set[date] = {ts.date() for kind, ts in rows if kind == "training"}
    streak = 0
    d = now.date()
    while d in training_days:
        streak += 1
        d = d - timedelta(days=1)

    return streak, last7, now
