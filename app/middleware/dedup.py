import os
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from app.storage import db as dbmod

_TTL = int(os.getenv("DEDUP_TTL_SEC", "900"))

class DedupMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Dict[str, Any], Any], Awaitable[Any]], event: Any, data: Dict[str, Any]):
        upd = data.get("event_update") or data.get("update") or getattr(event, "event", None)
        update_id = getattr(upd, "update_id", None)
        if update_id is not None:
            if dbmod.is_duplicate(int(update_id), _TTL):
                # Дубликат — гасим молча
                return
        return await handler(event, data)
