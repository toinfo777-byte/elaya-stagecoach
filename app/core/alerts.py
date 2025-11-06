# app/core/alerts.py
from __future__ import annotations

import asyncio
import hashlib
from typing import Optional

from aiogram import Bot
from pydantic import BaseModel

from app.config import settings


class Alert(BaseModel):
    title: str
    body: str = ""
    tag: str = "generic"  # для дедупликации по типу события


# простейший in-memory дедуп с TTL на процесс
# (для Render ок — нам важно отсечь повторы за короткое окно)
_dedup: dict[str, float] = {}
_lock = asyncio.Lock()


def _now() -> float:
    return asyncio.get_event_loop().time()


def _key(alert: Alert) -> str:
    s = f"{alert.tag}|{alert.title}|{alert.body}"
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


async def _is_duplicate(alert: Alert) -> bool:
    window = settings.alert_dedup_window_sec
    if window <= 0:
        return False
    k = _key(alert)
    async with _lock:
        t = _dedup.get(k)
        ts = _now()
        # очистка старья (дёшево, но хватает)
        if t is not None and ts - t < window:
            return True
        _dedup[k] = ts
        # фоновая очистка по времени
        for kk, vv in list(_dedup.items()):
            if ts - vv > window * 2:
                _dedup.pop(kk, None)
        return False


async def send_admin_alert(
    bot: Bot,
    title: str,
    body: str = "",
    tag: str = "generic",
    parse_mode: Optional[str] = "HTML",
) -> None:
    """Единая точка отправки алёртов в ADMIN_ALERT_CHAT_ID c дедупом."""
    chat_id = settings.admin_alert_chat_id
    if not chat_id:
        return

    alert = Alert(title=title, body=body, tag=tag)
    if await _is_duplicate(alert):
        return

    text = f"<b>{title}</b>"
    if body:
        text += f"\n{body}"
    try:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
    except Exception:
        # проглатываем — алёрты вторичны, не должны ронять воркер
        pass
