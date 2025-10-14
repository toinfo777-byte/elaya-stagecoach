# app/middlewares/throttling.py
from __future__ import annotations
import time
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, min_interval: float = 0.7) -> None:
        super().__init__()
        self.min_interval = min_interval
        self._last: Dict[str, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = None
        key = "generic"

        if isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id
            key = f"cb:{event.data or 'none'}"
        elif isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            # Для сообщений делаем мягче — один ключ на тип
            key = f"msg:{event.text or event.content_type}"

        if user_id is not None:
            now = time.monotonic()
            k = f"{user_id}:{key}"
            last = self._last.get(k, 0.0)
            if now - last < self.min_interval:
                # Тихо гасим дребезг колбэков; для сообщений — пропускаем
                if isinstance(event, CallbackQuery):
                    try:
                        await event.answer(cache_time=1)
                    except Exception:
                        pass
                return
            self._last[k] = now

        return await handler(event, data)
