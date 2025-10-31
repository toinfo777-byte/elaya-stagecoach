# app/middlewares/chat_scope.py
from __future__ import annotations

from typing import Callable, Awaitable, Any, Iterable, Optional, Set

from aiogram.enums import ChatType
from aiogram.types import Message, CallbackQuery, Chat
from aiogram import BaseMiddleware


def _chat_type(obj: Any) -> Optional[ChatType]:
    if isinstance(obj, Message):
        return obj.chat.type
    if isinstance(obj, CallbackQuery):
        if obj.message and obj.message.chat:
            return obj.message.chat.type
    return None


def _command_of(msg: Message) -> Optional[str]:
    """
    Возвращает команду вида '/menu' из текстового сообщения, если есть.
    """
    if not msg or not msg.text:
        return None
    txt = msg.text.strip()
    if not txt.startswith("/"):
        return None
    # отрезаем бот-суффикс /menu@BotName
    head = txt.split()[0]
    return head.split("@", 1)[0].lower()


class PrivateOnlyMiddleware(BaseMiddleware):
    """
    Глобальный фильтр области чатов.
    - В приватах пропускаем всё.
    - В группах/супергруппах пропускаем только allow-команды.
    Остальное — тихо игнорируем (без ответов), чтобы не "шуметь".
    """

    def __init__(self, allow_in_groups: Iterable[str] | None = None):
        self.allow: Set[str] = {s.lower() for s in (allow_in_groups or [])}

    async def __call__(
        self,
        handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        ctype = _chat_type(event)
        if ctype in (ChatType.PRIVATE,):
            return await handler(event, data)

        if ctype in (ChatType.GROUP, ChatType.SUPERGROUP):
            # Разрешаем только явные allow-команды
            msg = event if isinstance(event, Message) else (event.message if isinstance(event, CallbackQuery) else None)
            cmd = _command_of(msg) if isinstance(msg, Message) else None
            if cmd and cmd in self.allow:
                return await handler(event, data)
            # Группа: все остальные события — глушим
            return

        # каналы и прочее — тоже глушим
        return
