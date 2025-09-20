# app/bot/routers/privacy.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards.menu import main_menu, BTN_PRIVACY

router = Router(name="privacy")


@router.message(Command("privacy"))
@router.message(F.text == BTN_PRIVACY)
async def privacy_entry(message: Message) -> None:
    """
    Раздел «Политика конфиденциальности».
    """
    text = (
        "🔐 <b>Политика конфиденциальности</b>\n\n"
        "Мы храним минимум данных: ваш Telegram ID и ответы внутри бота.\n"
        "Данные используются для улучшения продукта и подсчёта прогресса.\n\n"
        "Удалить профиль и ответы — командой /wipe_me.\n"
        "Вернуться в меню — кнопка ниже."
    )
    await message.answer(text, reply_markup=main_menu(), parse_mode="HTML")
