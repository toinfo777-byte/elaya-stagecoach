# app/routers/leader.py
from __future__ import annotations

import logging
import inspect
from typing import Any

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="leader")
log = logging.getLogger("leader")

# --- безопасный импорт с fallback ---
try:
    from app.storage.repo_extras import save_leader_intent, save_premium_request  # type: ignore
except Exception as e:
    log.warning("repo_extras missing leader funcs, using fallbacks: %s", e)

    def save_leader_intent(user_id: int, intent: str, meta: dict | None = None) -> None:  # type: ignore
        log.info("[fallback] save_leader_intent(uid=%s, intent=%s, meta=%s)", user_id, intent, meta or {})

    def save_premium_request(
        user_id: int,
        plan: str,
        note: str | None = None,
        meta: dict | None = None,
    ) -> None:  # type: ignore
        log.info("[fallback] save_premium_request(uid=%s, plan=%s, note=%s, meta=%s)", user_id, plan, note, meta or {})

# --- универсальный вызов sync/async функций ---
async def _maybe_call(fn, *args: Any, **kwargs: Any) -> Any:
    """Если fn — coroutine function или возвращает awaitable — подождём; иначе вызовем синхронно."""
    if inspect.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    result = fn(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


@router.message(Command("leader"))
async def cmd_leader(message: Message):
    await message.reply("🏁 Путь лидера: пришли намерение текстом (например: «хочу в премиум»).")


@router.message(F.text)
async def any_text_as_intent(message: Message):
    intent = (message.text or "").strip()
    if not intent:
        return
    await _maybe_call(save_leader_intent, message.from_user.id, intent, meta={"source": "text"})
    await message.reply("✅ Намерение зафиксировано.")


@router.message(Command("premium"))
async def cmd_premium(message: Message):
    await _maybe_call(save_premium_request, message.from_user.id, plan="premium", meta={"source": "command"})
    await message.reply("✨ Заявка на премиум зафиксирована.")
