from __future__ import annotations
from aiogram import Bot
from app.control.admin import alert_targets

async def notify_admins(bot: Bot, text: str) -> int:
    """Разослать сообщение всем целям. Возвращает число доставок (best-effort)."""
    delivered = 0
    for chat_id in alert_targets():
        try:
            await bot.send_message(chat_id, text)
            delivered += 1
        except Exception:
            # молча пропускаем, чтобы одно падение не ломало рассылку
            pass
    return delivered
