# app/routers/extended.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_EXTENDED
from app.utils.admin import notify_admin

router = Router(name="extended")

EXT_TEXT = (
    "⭐ Расширенная версия:\n"
    "• Больше сценариев\n"
    "• Персональные разборы\n"
    "• Расширенная метрика прогресса\n\n"
    "Если интересно — напиши «Хочу расширенную»."
)


@router.message(Command("extended"))
@router.message(F.text == BTN_EXTENDED)
async def extended_info(msg: Message):
    await msg.answer(EXT_TEXT)


@router.message(F.text.regexp("(?i)^хочу расширенную"))
async def extended_interest(msg: Message):
    await notify_admin(
        msg.bot,
        f"⭐ Заявка на расширенную: @{msg.from_user.username or msg.from_user.id}",
    )
    await msg.answer(
        "Принято! Менеджер свяжется с тобой. Возвращаю меню.",
        reply_markup=main_menu(),
    )
