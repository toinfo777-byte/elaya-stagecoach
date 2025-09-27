# app/routers/extended.py
from __future__ import annotations

import os
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from app.keyboards.reply import main_menu_kb, BTN_EXTENDED

router = Router(name="extended")

EXTENDED_PITCH = (
    "⭐ Расширенная версия:\n"
    "• Больше сценариев тренировки\n"
    "• Персональные разборы\n"
    "• Расширенная метрика прогресса\n\n"
    "Хочешь доступ? Напиши «Хочу расширенную»."
)

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_CHAT_IDS", "").split(",") if x.strip()]

@router.message(StateFilter("*"), Command("extended"))
@router.message(StateFilter("*"), F.text == BTN_EXTENDED)
async def extended_pitch(m: Message):
    await m.answer(EXTENDED_PITCH, reply_markup=main_menu_kb())

@router.message(F.text.regexp("(?i)^хочу расширенную"))
async def extended_request(m: Message):
    for admin_id in ADMIN_IDS:
        try:
            await m.bot.send_message(
                admin_id,
                f"⭐ Запрос расширенной версии от @{m.from_user.username or m.from_user.id}",
            )
        except Exception:
            pass
    await m.answer("✅ Запрос принят. Мы свяжемся с тобой.", reply_markup=main_menu_kb())
