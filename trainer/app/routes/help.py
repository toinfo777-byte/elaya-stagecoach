from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message

from app.keyboards.main_menu import MAIN_MENU


router = Router(name="help")


HELP_TEXT = """<b>Помощь</b>

Этот бот — тренер сцены Элайя. Он помогает развивать голос, дыхание, внимание и уверенность через короткие тренировки.

<b>Что можно делать сейчас:</b>
• запускать базовые тренировки дня через «🎭 Тренировка дня»;
• отслеживать прогресс через «📋 Мой прогресс»;
• оставлять отзывы и замечания.

Если что-то работает странно — просто напиши об этом в отзыве или сообщении.
"""


@router.message(
    (F.text == "/help")
    | (F.text == "/help@ElayaTrainerDevBot")
    | (F.text == "💬 Помощь")
)
async def handle_help(message: Message) -> None:
    """
    Один и тот же хендлер на:
    - команду /help
    - команду /help@ElayaTrainerDevBot
    - кнопку «💬 Помощь»
    """
    await message.answer(HELP_TEXT, reply_markup=MAIN_MENU)
