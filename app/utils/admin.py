# app/utils/admin.py
import os
from aiogram import Bot

# ID чата/канала, куда слать алерты (берётся из ENV)
ADMIN_ALERT_CHAT_ID = int(os.getenv("ADMIN_ALERT_CHAT_ID", "0"))


async def notify_admin(text: str, bot: Bot | None = None) -> None:
    """
    Отправляет сообщение админу, если задан ADMIN_ALERT_CHAT_ID.
    Передавай bot явно из контекста (например, message.bot).
    """
    if ADMIN_ALERT_CHAT_ID and bot:
        try:
            await bot.send_message(ADMIN_ALERT_CHAT_ID, text)
        except Exception as e:
            # Чтобы не падать, если бот не имеет прав или чат не найден
            print(f"[notify_admin] Ошибка отправки: {e}")
