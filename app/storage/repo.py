# app/storage/repo.py
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import date, timedelta
from typing import Optional, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.models import Base, engine, async_session_maker, TrainingLog  # важно: engine + async_session_maker

log = logging.getLogger("db")


def ensure_schema() -> None:
    """
    Создаёт таблицы (если их нет). Вызывается из main.py перед стартом polling.
    Работает поверх async-движка, но удобен для синхронного вызова.
    """
    async def _run():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        log.info("✅ БД инициализирована")

    # Запускаем вне существующего цикла/внутри — безопасно
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(_run())
    else:
        loop.create_task(_run())


@asynccontextmanager
async def get_session() -> AsyncSession:
    """
    Унифицированный способ получить AsyncSession.
    """
    async with async_session_maker() as session:
        yield session


# === Async repo API (для FSM-сценариев MVP) ==================================

async def repo_add_training_entry(user_id: int, day: date, level: str, done: bool):
    """
    Добавляет запись о тренировке пользователя.
    """
    async with async_session_maker() as s:
        row = TrainingLog(user_id=user_id, day=day, level=level, done=done)
        s.add(row)
        await s.commit()


async def repo_get_today_training(user_id: int, day: date) -> Optional[TrainingLog]:
    """Запись тренировки за конкретный день (если есть)."""
    async with async_session_maker() as s:
        q = (
            select(TrainingLog)
            .where(TrainingLog.user_id == user_id, TrainingLog.day == day)
            .order_by(TrainingLog.id.desc())
            .limit(1)
        )
        res = await s.execute(q)
        return res.scalar_one_or_none()


async def repo_get_stats(user_id: int, since: Optional[date] = None) -> Dict[str, object]:
    """Сводка по тренировкам: всего / выполнено / пропусков / % выполнения."""
    today = date.today()
    if since is None:
        since = today - timedelta(days=29)

    async with async_session_maker() as s:
        q = (
            select(TrainingLog)
            .where(
                TrainingLog.user_id == user_id,
                TrainingLog.day >= since,
                TrainingLog.day <= today,
            )
            .order_by(TrainingLog.day.asc(), TrainingLog.id.asc())
        )
        res = await s.execute(q)
        rows: List[TrainingLog] = list(res.scalars())

    total = len(rows)
    done = sum(1 for r in rows if r.done)
    skipped = sum(1 for r in rows if not r.done)
    rate = (done / total * 100.0) if total else 0.0

    return {
        "total": total,
        "done": done,
        "skipped": skipped,
        "completion_rate": round(rate, 1),
        "since": since,
        "until": today,
    }


async def repo_get_streak(user_id: int) -> int:
    """Текущая непрерывная полоса выполнений (done=True), считая от сегодня назад."""
    today = date.today()
    async with async_session_maker() as s:
        q = (
            select(TrainingLog)
            .where(TrainingLog.user_id == user_id, TrainingLog.done.is_(True))
            .order_by(TrainingLog.day.desc(), TrainingLog.id.desc())
            .limit(120)
        )
        res = await s.execute(q)
        rows: List[TrainingLog] = list(res.scalars())

    done_days = {r.day for r in rows}
    streak = 0
    d = today
    while d in done_days:
        streak += 1
        d -= timedelta(days=1)
    return streak


async def repo_get_calendar(user_id: int, start: date, end: date) -> Dict[date, str]:
    """Календарь: 'done' | 'skip' | 'none' за период [start; end]."""
    async with async_session_maker() as s:
        q = (
            select(TrainingLog)
            .where(
                TrainingLog.user_id == user_id,
                TrainingLog.day >= start,
                TrainingLog.day <= end,
            )
        )
        res = await s.execute(q)
        rows: List[TrainingLog] = list(res.scalars())

    status: Dict[date, str] = {}
    for r in rows:
        prev = status.get(r.day)
        if r.done:
            status[r.day] = "done"
        else:
            if prev != "done":
                status[r.day] = "skip"

    d = start
    one = timedelta(days=1)
    while d <= end:
        status.setdefault(d, "none")
        d += one

    return status
