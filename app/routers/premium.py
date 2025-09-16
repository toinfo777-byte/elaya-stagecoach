from __future__ import annotations

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message

from app.routers.menu import BTN_PREMIUM, main_menu

router = Router(name="premium")

@router.message(StateFilter("*"), lambda x: x.text == BTN_PREMIUM)
async def btn_premium(m: Message):
    await m.answer(
        "⭐️ Расширенная версия — скоро. Оставь заявку в /apply, чтобы узнать первым.",
        reply_markup=main_menu(),
    )
