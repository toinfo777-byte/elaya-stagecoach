import os
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery

# список разрешённых групповых команд: "/hq,/healthz"
ALLOW = {s.strip() for s in os.getenv("ALLOW_GROUP_COMMANDS", "").split(",") if s.strip()}

class GroupGate(BaseMiddleware):
    """
    Режет ВСЕ групповые апдейты, кроме явно разрешённых команд.
    Работает и для message, и для callback_query (на всякий случай).
    """
    async def __call__(self, handler, event: Update, data):
        msg: Message | None = None
        if isinstance(event, Message):
            msg = event
        elif isinstance(event, CallbackQuery):
            msg = event.message

        if not msg:
            return await handler(event, data)

        chat_type = getattr(msg.chat, "type", "private")
        if chat_type in ("group", "supergroup"):
            text = (msg.text or msg.caption or "").strip()
            # пропускаем только если сообщение начинается с одной из разрешённых команд
            if not any(text.startswith(cmd) for cmd in ALLOW):
                return  # молча отсекаем
        return await handler(event, data)
