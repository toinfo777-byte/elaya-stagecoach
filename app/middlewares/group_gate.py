from __future__ import annotations

from typing import Callable, Awaitable, Dict, Any, Iterable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Chat, ChatType


def _extract_command(m: Message) -> str | None:
    """
    Возвращает команду в виде '/xxx' без '@username', если она есть в тексте.
    Работает корректно для /cmd и /cmd@Bot.
    """
    if not m.text or not m.entities:
        return None
    for ent in m.entities:
        if ent.type == "bot_command":
            raw = m.text[ent.offset : ent.offset + ent.length]
            return raw.split("@", 1)[0]  # '/menu@Bot' -> '/menu'
    return None


class GroupCommandGate(BaseMiddleware):
    """
    Режим: в группах пропускаем только команды из whitelist.
    Всё остальное — глушим, не передаём хендлерам.
    В личке — не вмешиваемся.
    """

    def __init__(self, allowed_commands: Iterable[str]):
        self.allowed = {c.strip() for c in allowed_commands if c and c.strip()}

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        # Нормализуем до Message
        msg: Message | None
        if isinstance(event, CallbackQuery):
            msg = event.message
        elif isinstance(event, Message):
            msg = event
        else:
            msg = None

        if msg is None:
            return await handler(event, data)

        # Фильтруем только группы
        if msg.chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
            cmd = _extract_command(msg)
            if cmd and cmd in self.allowed:
                return await handler(event, data)
            # Глушим всё остальное (включая /menu, /start и т.п.)
            return

        # Личные — пропускаем
        return await handler(event, data)
