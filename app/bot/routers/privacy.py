# app/bot/routers/privacy.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

# единый источник текстов кнопок и меню
from app.keyboards.menu import main_menu, BTN_PRIVACY

router = Router(name="privacy")

PRIVACY_TEXT = (
    "🛡 <b>Политика конфиденциальности</b>\n\n"
    "Мы храним минимум данных: ваш Telegram ID и ответы внутри бота.\n"
    "Командой <code>/wipe_me</code> профиль и записи можно удалить.\n"
    "Данные отзывов и прогресса используются для улучшения продукта."
)

@router.message(Command("privacy"))
@router.message(F.text == BTN_PRIVACY)             # 🛡 Политика (из константы)
@router.message(F.text.endswith("Политика"))       # на всякий случай — если эмодзи отличится
async def privacy_entry(message: Message) -> None:
    await message.answer(PRIVACY_TEXT, reply_markup=main_menu())
