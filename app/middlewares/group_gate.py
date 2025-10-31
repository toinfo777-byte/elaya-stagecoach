from __future__ import annotations
from typing import Callable, Awaitable, Dict, Any, Iterable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, ChatType


def extract_command(text: str | None) -> str | None:
    """Извлекает /command без @username."""
    if not text:
        return None
    if not text.startswith("/"):
        return None
    cmd = text.split()[0]
    return cmd.split("@", 1)[0]  # '/menu@Bot' → '/menu'


class GroupCommandGate(BaseMiddleware):
    """
    Глушит всё, что приходит из групп/супергрупп.
    Разрешает только команды из whitelist (например: /hq, /healthz).
    Даже если команда без @username и даже если reply.
    """

    def __init__(self, allowed: Iterable[str]):
        self.allowed = {a.strip() for a in allowed if a.strip()}

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        message: Message | None = None

        if isinstance(event, Message):
            message = event
        elif isinstance(event, CallbackQuery):
            message = event.message

        if not message:
            return await handler(event, data)

        # Только для групп
        if message.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
            text = (message.text or message.caption or "").strip()
            cmd = extract_command(text)

            # Разрешаем только whitelisted-команды
            if cmd and cmd in self.allowed:
                return await handler(event, data)

            # Всё остальное глушим
            return

        # Приватные чаты — всё разрешено
        return await handler(event, data)
