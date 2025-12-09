# trainer/app/routes/faq.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU

router = Router(name="faq")

HELP_TEXT = (
    "🧾 <b>Помощь</b>\n\n"
    "Этот бот — тренер сцены Элайя.\n"
    "Он помогает развивать голос, дыхание, внимание и уверенность через короткие тренировки.\n\n"
    "<b>Что можно делать сейчас:</b>\n"
    "• запускать базовые тренировки дня;\n"
    "• отслеживать прогресс через «📈 Мой прогресс»;\n"
    "• оставлять отзывы и замечания.\n\n"
    "Если что-то работает странно — просто напиши об этом в отзыве или сообщении."
)


@router.message(F.text == "💬 Помощь")
async def handle_help_button(message: Message) -> None:
    """Обработка нажатия кнопки в клавиатуре."""
    await message.answer(HELP_TEXT, reply_markup=MAIN_MENU)


@router.message(F.text.in_({"/help", "help", "/faq"}))
async def handle_help_command(message: Message) -> None:
    """Запасной вариант — команды /help, /faq."""
    await message.answer(HELP_TEXT, reply_markup=MAIN_MENU)
