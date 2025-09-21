# app/storage/repo.py
from __future__ import annotations

import os
import logging
from contextlib import contextmanager
from typing import Iterator
from datetime import date, timedelta
from typing import Optional, Dict, List

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.engine.url import make_url, URL
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.storage.models import Base, async_session_maker, TrainingLog

log = logging.getLogger("db")


def _resolve_db_url(raw: str) -> str:
    """
    Чиним SQLite путь:
    - если каталог недоступен для записи — переносим файл в /tmp
    - создаём каталог при необходимости
    Для остальных диалектов возвращаем как есть.
    """
    url: URL = make_url(raw)
    if url.get_backend_name() != "sqlite":
        return raw

    db_path = url.database or ""
    if db_path in ("", ":memory:"):
        return raw

    abs_path = db_path if os.path.isabs(db_path) else os.path.abspath(db_path)
    target_dir = os.path.dirname(abs_path) or "."

    def _writable_dir(path: str) -> bool:
        try:
            os.makedirs(path, exist_ok=True)
            testfile = os.path.join(path, ".write_test")
            with open(testfile, "w") as f:
                f.write("ok")
            os.remove(testfile)
            return True
        except Exception:
            return False

    if not _writable_dir(target_dir):
        log.warning("DB dir '%s' недоступна для записи. Переношу БД в /tmp", target_dir)
        base = os.path.basename(abs_path) or "elaya.db"
        abs_path = os.path.join("/tmp", base)
        os.makedirs("/tmp", exist_ok=True)

    fixed = url.set(database=abs_path)
    return str(fixed)


DB_URL = _resolve_db_url(settings.db_url)

engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


@contextmanager
def session_scope() -> Iterator:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def ensure_schema() -> None:
    """
    Создаёт отсутствующие таблицы. Идемпотентно.
    """
    insp = inspect(engine)
    if not insp.has_table("users"):
        Base.metadata.create_all(bind=engine)
    log.info("✅ БД инициализирована (%s)", DB_URL)


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
