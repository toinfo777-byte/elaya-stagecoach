# app/routers/leader.py
from __future__ import annotations

import logging
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


@router.message(Command("leader"))
async def cmd_leader(message: Message):
    await message.reply("🏁 Путь лидера: выбери намерение из меню или пришли текстом.\nНапр.: <code>хочу в премиум</code>")

# Пример: простой приём текста как «намерение»
@router.message(F.text)
async def any_text_as_intent(message: Message):
    intent = (message.text or "").strip()
    if not intent:
        return
    save_leader_intent(message.from_user.id, intent, meta={"source": "text"})
    await message.reply("✅ Намерение зафиксировано.")

# Пример: фиксация запроса на премиум через команду
@router.message(Command("premium"))
async def cmd_premium(message: Message):
    save_premium_request(message.from_user.id, plan="premium", meta={"source": "command"})
    await message.reply("✨ Заявка на премиум зафиксирована.")
