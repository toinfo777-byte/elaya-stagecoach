from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message

router = Router(name="panic")

@router.message(F.text.in_({"/panic", "panic"}))
async def cmd_panic(msg: Message):
    await msg.answer("⚠️ Провожу тест ошибки для Sentry…")
    raise RuntimeError("Test panic — Sentry integration check")
