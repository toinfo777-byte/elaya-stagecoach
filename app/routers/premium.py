from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.routers.menu import BTN_PREMIUM, main_menu

router = Router(name="premium")

@router.message(Command("premium"))
@router.message(F.text == BTN_PREMIUM)
async def premium_entry(m: Message):
    await m.answer("⭐️ Расширенная версия: скоро! Мы готовим дополнительные фичи.", reply_markup=main_menu())
