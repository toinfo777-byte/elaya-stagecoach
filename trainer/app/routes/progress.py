from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

import httpx
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.core_api import CORE_URL

router = Router(name="progress")

PROGRESS_BUTTON_TEXT = "📈 Мой прогресс"


async def _fetch_timeline(limit: int = 365) -> List[Dict[str, Any]]:
    """
    Забираем события из ядра через /api/timeline.
    """
    if not CORE_URL:
        print("WARN: TRAINER_CORE_URL not set, skip timeline fetch")
        return []

    url = f"{CORE_URL.rstrip('/')}/api/timeline"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url, params={"limit": limit})
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        print("ERROR fetching timeline:", repr(e))
        return []

    events = data.get("events", [])
    if isinstance(events, list):
        return events
    return []


def _parse_ts(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except Exception:
        # в крайнем случае — берём сейчас, чтобы не падать
        return datetime.now(timezone.utc)


def _build_progress_text(events: List[Dict[str, Any]]) -> str:
    """
    Строим человекочитаемый отчёт по событиям тренера.
    Считаем только завершённые тренировки (trainer:day:review).
    """
    reviews = [e for e in events if e.get("scene") == "trainer:day:review"]
    if not reviews:
        return (
            "📈 Пока нет завершённых тренировок.\n\n"
            "Нажми «🎭 Тренировка дня», чтобы начать первую."
        )

    # сортируем по времени
    reviews_sorted = sorted(reviews, key=lambda e: _parse_ts(e.get("ts", "")))
    total = len(reviews_sorted)

    # дни, когда были тренировки
    dates = [_parse_ts(e.get("ts", "")).date() for e in reviews_sorted]
    unique_dates = sorted(set(dates))
    dates_set = set(unique_dates)

    # считаем текущую серию по дням (от сегодняшнего дня назад)
    today = datetime.now(timezone.utc).date()
    streak = 0
    current = today
    while current in dates_set:
        streak += 1
        current -= timedelta(days=1)

    # последняя тренировка
    last = reviews_sorted[-1]
    last_ts = _parse_ts(last.get("ts", ""))
    payload = last.get("payload", {}) or {}
    review_text = payload.get("review") or "без текста"
    transition = payload.get("transition") or "без формулировки"
    reflect = payload.get("reflect") or None

    lines: List[str] = [
        "📈 Твой прогресс",
        "",
        f"Всего завершено тренировок: <b>{total}</b>",
        f"Текущая серия по дням: <b>{streak}</b>",
        "",
        "🕒 Последняя тренировка:",
        f"• дата: {last_ts.date().isoformat()}",
        f"• отзыв: {review_text}",
        f"• вектор дня: {transition}",
    ]
    if reflect:
        lines.append(f"• отражение: {reflect}")

    lines.append("")
    lines.append("Если захочешь — в любой день нажимай «🎭 Тренировка дня».")

    return "\n".join(lines)


@router.message(Command("progress"))
@router.message(F.text == PROGRESS_BUTTON_TEXT)
async def handle_progress(message: Message) -> None:
    """
    Хэндлер кнопки «📈 Мой прогресс» и команды /progress.
    Берёт таймлайн ядра и показывает живой отчёт.
    """
    events = await _fetch_timeline(limit=365)
    text = _build_progress_text(events)
    await message.answer(text)
