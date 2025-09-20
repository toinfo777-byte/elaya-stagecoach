from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_PREMIUM, BTN_APPLY

router = Router(name="premium")


@router.message(Command("premium"))
@router.message(F.text == BTN_PREMIUM)
async def premium_entry(message: Message) -> None:
    text = (
        "<b>Расширенная версия</b>\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и «путь лидера»\n\n"
        f"Нажми «{BTN_APPLY}», чтобы оставить заявку."
    )
    await message.answer(text, reply_markup=main_menu())
