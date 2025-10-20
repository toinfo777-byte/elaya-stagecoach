# app/control/admin.py
from __future__ import annotations

import os
from typing import Iterable, Set

from aiogram.filters import BaseFilter
from aiogram.types import Message

def _parse_ids(raw: str | None) -> Set[int]:
    if not raw:
        return set()
    parts: Iterable[str] = (p.strip() for p in raw.replace(";", ",").split(","))
    return {int(p) for p in parts if p}

ADMIN_ALERT_CHAT_ID = os.getenv("ADMIN_ALERT_CHAT_ID")
ADMIN_IDS: Set[int] = _parse_ids(os.getenv("ADMIN_IDS"))

def is_admin(user_id: int | None) -> bool:
    if user_id is None:
        return False
    if ADMIN_ALERT_CHAT_ID and int(ADMIN_ALERT_CHAT_ID) == user_id:
        return True
    return user_id in ADMIN_IDS

class AdminOnly(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return is_admin(message.from_user.id if message.from_user else None)
