# app/middlewares/error_handler.py
from __future__ import annotations

import logging
from typing import Any, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

log = logging.getLogger(__name__)

class ErrorsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as exc:  # noqa: BLE001
            # — формат: level=ERROR | router | user | exc
            router_name = ""
            try:
                router = data.get("event_router")
                router_name = getattr(router, "name", "") or str(router)
            except Exception:
                router_name = ""

            user_id = None
            try:
                if isinstance(event, Message):
                    user_id = event.from_user.id if event.from_user else None
                elif isinstance(event, CallbackQuery):
                    user_id = event.from_user.id if event.from_user else None
            except Exception:
                pass

            log.exception("level=ERROR | router=%s | user=%s | exc=%s", router_name, user_id, exc)

            # Пользователю — единый шаблон
            try:
                if isinstance(event, Message):
                    await event.answer("Ой, что-то пошло не так. Повтори шаг или вернись в меню: /menu 🙏")
                elif isinstance(event, CallbackQuery):
                    await event.message.answer("Ой, что-то пошло не так. Повтори шаг или вернись в меню: /menu 🙏")
            except Exception:
                pass
            # не проглатываем полностью — пусть aiogram не рушится, но ошибку мы уже залогировали
            return None
