from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards.menu import main_menu, BTN_PREMIUM

router = Router(name="premium")

INFO = (
    "<b>Расширенная версия</b>\n\n"
    "• Ежедневный разбор и обратная связь\n"
    "• Разогрев голоса, дикции и внимания\n"
    "• Мини-кастинг и «путь лидера»\n\n"
    "Нажми «🧭 Путь лидера», чтобы оставить заявку."
)

@router.message(Command("premium"))
@router.message(F.text == BTN_PREMIUM)
async def premium_entry(message: Message) -> None:
    await message.answer(INFO, reply_markup=main_menu())
