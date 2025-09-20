from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.keyboards.menu import main_menu, BTN_PRIVACY

router = Router(name="privacy")

# Поддержим старые варианты иконок/текстов
PRIVACY_ALIASES = {BTN_PRIVACY, "🛡 Политика", "Политика", "/privacy"}

TEXT = (
    "<b>Политика конфиденциальности</b>\n\n"
    "Мы храним минимум данных: ваш Telegram ID и ответы внутри бота.\n"
    "Командой <code>/wipe_me</code> профиль и записи можно удалить.\n"
    "Данные отзывов и прогресса используются для улучшения продукта."
)

@router.message(Command("privacy"))
@router.message(F.text.in_(PRIVACY_ALIASES))
async def show_privacy(message: Message) -> None:
    await message.answer(TEXT, reply_markup=main_menu())
