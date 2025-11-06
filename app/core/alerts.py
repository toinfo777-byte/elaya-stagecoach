from __future__ import annotations

import os
import time
import asyncio
from typing import Optional
from aiogram import Bot

# ── настройки алертов из ENV ───────────────────────────────────────────────────
_ADMIN_CHAT_ENV = "ADMIN_ALERT_CHAT_ID"           # ID админ-группы
_DEDUP_WINDOW = max(1, int(os.getenv("ALERT_DEDUP_WINDOW_SEC", "15")))
_SOURCE = os.getenv("ALERT_SOURCE", "web")        # 'web' | 'trainer' | ...
ALERT_ENABLED = os.getenv("ALERT_ENABLED", "1") not in ("0", "false", "False")

# ── состояние процесса (in-memory) ─────────────────────────────────────────────
_admin_chat_id_cached: Optional[int] = None
_last_sent: dict[str, float] = {}
_lock = asyncio.Lock()


def _admin_chat_id() -> int:
    """Ленивая загрузка chat_id из ENV с кэшем."""
    global _admin_chat_id_cached
    if _admin_chat_id_cached is None:
        raw = os.getenv(_ADMIN_CHAT_ENV, "").strip()
        if not raw:
            raise RuntimeError(f"{_ADMIN_CHAT_ENV} is not set")
        _admin_chat_id_cached = int(raw)
    return _admin_chat_id_cached


def _now() -> float:
    return time.monotonic()


async def _should_send(key: str) -> bool:
    """Дедупликация по ключу на окно времени."""
    now = _now()
    async with _lock:
        ts = _last_sent.get(key, 0.0)
        if now - ts < _DEDUP_WINDOW:
            return False
        _last_sent[key] = now
        # редкая лениво-чистка
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
    По умолчанию ключ = f"{_SOURCE}:{text[:120]}" — отсекает повторы
    от разных сервисов за окно времени.
    """
    if not ALERT_ENABLED:
        return False

    # тренер по умолчанию НЕ шлёт в общий админ-чат
    if _SOURCE == "trainer":
        return False

    key = dedup_key or f"{_SOURCE}:{text[:120]}"
    if not await _should_send(key):
        return False

    await bot.send_message(_admin_chat_id(), text, parse_mode=parse_mode)
    return True
