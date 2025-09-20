from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_PRIVACY

router = Router(name="privacy")


@router.message(Command("privacy"))
@router.message(F.text == BTN_PRIVACY)
async def privacy_entry(message: Message) -> None:
    text = (
        "<b>Политика конфиденциальности</b>\n\n"
        "Мы храним минимум данных: ваш Telegram ID и ответы внутри бота.\n"
        "Командой <code>/wipe_me</code> профиль и записи можно удалить.\n"
        "Данные отзывов и прогресса используются для улучшения продукта."
    )
    await message.answer(text, reply_markup=main_menu())
