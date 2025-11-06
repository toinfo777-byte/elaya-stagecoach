from __future__ import annotations

import os
import time
import asyncio
from typing import Optional

from aiogram import Bot

# Куда слать алерты
_ADMIN_CHAT_ID: Optional[int] = None
# Окно дедупликации (сек)
_DEDUP_WINDOW = max(1, int(os.getenv("ALERT_DEDUP_WINDOW_SEC", "15")))
# Маркер источника (web|bot|trainer)
_SOURCE = os.getenv("ALERT_SOURCE", "web")

# Память процесса: ключ -> ts последней отправки
_last_sent: dict[str, float] = {}
_lock = asyncio.Lock()


def _admin_chat_id() -> int:
    """Лениво получаем ID админ-чата из ENV."""
    global _ADMIN_CHAT_ID
    if _ADMIN_CHAT_ID is None:
        raw = (os.getenv("ADMIN_ALERT_CHAT_ID") or "").strip()
        if not raw:
            raise RuntimeError("ADMIN_ALERT_CHAT_ID is not set")
        _ADMIN_CHAT_ID = int(raw)
    return _ADMIN_CHAT_ID


def _now() -> float:
    return time.monotonic()


async def _should_send(key: str) -> bool:
    """Дедупликация сообщений в рамках процесса."""
    now = _now()
    async with _lock:
        ts = _last_sent.get(key, 0.0)
        if now - ts < _DEDUP_WINDOW:
            return False
        _last_sent[key] = now
        # Ленивая чистка
        if len(_last_sent) > 256:
            cutoff = now - (_DEDUP_WINDOW * 2)
            for k, v in list(_last_sent.items()):
                if v < cutoff:
                    _last_sent.pop(k, None)
        return True


async def send_admin_alert(
    bot: Bot,
    text: str,
    *,
    dedup_key: Optional[str] = None,
    parse_mode: Optional[str] = "HTML",
) -> bool:
    """
    Отправляет алерт в админ-чат с дедупликацией.
    По умолчанию ключ = f"{_SOURCE}:{text[:120]}" — это убирает дубли,
    приходящие из разных сервисов за заданное окно.
    """
    key = dedup_key or f"{_SOURCE}:{text[:120]}"
    if not await _should_send(key):
        return False
    if os.getenv("ALERT_SOURCE", "web") == "trainer":
    return True  # тренер не шлёт в общий чат
await bot.send_message(_admin_chat_id(), text, parse_mode=parse_mode)

