# app/core/alerts.py
import time
from collections import deque
from typing import Optional
from aiogram import Bot
from app.config import settings

# простая ТТL-дедупликация
_DEDUP_WINDOW = settings.alert_dedup_window_sec
_recent: deque[tuple[str, float]] = deque()  # (key, ts)

def _seen(key: str) -> bool:
    now = time.time()
    # чистим старое
    while _recent and now - _recent[0][1] > _DEDUP_WINDOW:
        _recent.popleft()
    # проверяем
    for k, _ in _recent:
        if k == key:
            return True
    _recent.append((key, now))
    return False

async def send_admin_alert(bot: Bot, text: str, dedup_key: Optional[str] = None) -> None:
    chat_id = settings.admin_alert_chat_id
    if not chat_id:
        return
    if dedup_key and _seen(dedup_key):
        return
    await bot.send_message(chat_id, text)
