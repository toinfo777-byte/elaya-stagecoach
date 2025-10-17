# app/control/notifier.py
from __future__ import annotations

import os
from aiogram import Bot

ADMIN_ALERT_CHAT_ID = (os.getenv("ADMIN_ALERT_CHAT_ID") or "").strip()


async def notify_admins(bot: Bot, text: str) -> bool:
    if not ADMIN_ALERT_CHAT_ID:
        return False
    try:
        await bot.send_message(ADMIN_ALERT_CHAT_ID, text)
        return True
    except Exception:
        return False
