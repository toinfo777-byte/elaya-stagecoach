from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.keyboards.menu import main_menu, (
    BTN_HELP, BTN_TRAIN, BTN_PROGRESS, BTN_APPLY, BTN_CASTING,
    BTN_PRIVACY, BTN_PREMIUM, BTN_SETTINGS,
)

router = Router(name="help")

@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def help_entry(message: Message) -> None:
    text = (
        "<b>Помощь</b>\n\n"
        "Команды:\n"
        "/start — Начать / онбординг\n"
        "/menu — Открыть меню\n"
        "/training — Тренировка дня\n"
        "/progress — Мой прогресс\n"
        "/apply — Путь лидера (заявка)\n"
        "/casting — Мини-кастинг\n"
        "/privacy — Политика конфиденциальности\n"
        "/premium — Расширенная версия\n"
        "/settings — Настройки"
    )
    await message.answer(text, reply_markup=main_menu())
