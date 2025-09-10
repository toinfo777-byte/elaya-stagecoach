# app/middlewares/source_tags.py
from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Any, Dict, Callable

from app.storage.repo import session_scope
from app.storage.models import User

# Нормализация источника
def detect_source_text(event: TelegramObject) -> str:
    txt = None
    if isinstance(event, Message):
        txt = (event.text or "").strip() if event.text else ""
        if txt.startswith("/"):
            # команда
            cmd = txt.split()[0]
            return f"cmd:{cmd}"
        if txt:
            return f"text:{txt[:32]}"
        return "message"
    if isinstance(event, CallbackQuery):
        data = event.data or ""
        return f"cb:{data[:32]}"
    return "event"

class SourceTagsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            # получаем tg_id
            tg_id = None
            if isinstance(event, Message):
                tg_id = event.from_user.id if event.from_user else None
            elif isinstance(event, CallbackQuery):
                tg_id = event.from_user.id if event.from_user else None

            if tg_id:
                src = detect_source_text(event)
                with session_scope() as s:
                    u = s.query(User).filter_by(tg_id=tg_id).first()
                    if u and hasattr(u, "meta_json"):
                        meta = dict(u.meta_json or {})
                        sources = dict(meta.get("sources", {}))
                        if "first_source" not in sources:
                            sources["first_source"] = src
                        sources["last_source"] = src
                        meta["sources"] = sources
                        u.meta_json = meta
                        s.add(u)
                        s.commit()
        except Exception:
            # не блокируем пайплайн, если апдейт метки не удался
            pass

        return await handler(event, data)
