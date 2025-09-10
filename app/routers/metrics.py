# app/routers/metrics.py
from __future__ import annotations
from datetime import datetime, timedelta, timezone

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.config import settings
from app.storage.repo import session_scope
from app.storage.models import Event  # предполагается таблица events с полями type, user_id, created_at

router = Router(name="metrics")

def _is_admin(uid: int) -> bool:
    admin_ids = getattr(settings, "admin_ids", []) or []
    return uid in admin_ids

def _day_range_utc(days_ago: int):
    # [start, end) в UTC
    today = datetime.now(timezone.utc).date()
    day = today - timedelta(days=days_ago)
    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return start, end

def _count(s, etype: str, start, end) -> int:
    return s.query(Event).filter(
        Event.type == etype,
        Event.created_at >= start,
        Event.created_at < end,
    ).count()

@router.message(StateFilter("*"), Command("metrics"))
async def metrics_cmd(m: Message):
    if not _is_admin(m.from_user.id):
        return

    with session_scope() as s:
        # сегодня
        s0, e0 = _day_range_utc(0)
        started0 = _count(s, "started_training", s0, e0)
        finished0 = _count(s, "finished_training", s0, e0)
        conv0 = f"{(finished0 / started0 * 100):.0f}%" if started0 else "—"

        # вчера
        s1, e1 = _day_range_utc(1)
        started1 = _count(s, "started_training", s1, e1)
        finished1 = _count(s, "finished_training", s1, e1)
        conv1 = f"{(finished1 / started1 * 100):.0f}%" if started1 else "—"

        coach_on0 = _count(s, "coach_on", s0, e0)
        feedback0 = _count(s, "feedback_added", s0, e0)

    txt = (
        "📊 *Мини-метрики*\n\n"
        f"*Сегодня*\n"
        f"• Начали тренировку: {started0}\n"
        f"• Закончили тренировку: {finished0}\n"
        f"• Конверсия: {conv0}\n"
        f"• coach_on: {coach_on0}\n"
        f"• feedback_added: {feedback0}\n\n"
        f"*Вчера*\n"
        f"• Начали тренировку: {started1}\n"
        f"• Закончили тренировку: {finished1}\n"
        f"• Конверсия: {conv1}\n"
    )
    await m.answer(txt, parse_mode="Markdown")
