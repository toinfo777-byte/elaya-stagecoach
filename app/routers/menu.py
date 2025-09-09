# app/routers/menu.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# Берём текст политики из texts (если файла нет — будет запасной текст)
try:
    from app.texts.strings import PRIVACY_TEXT
except Exception:  # запасной вариант, чтобы импорт не падал
    PRIVACY_TEXT = (
        "Политика обработки персональных данных: текст будет размещён здесь. "
        "Если вы видите это сообщение — заглушка активна."
    )

router = Router(name="menu")


def main_menu() -> ReplyKeyboardMarkup:
    """Главное меню (reply-клавиатура)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏋️ Тренировка"), KeyboardButton(text="🎭 Мини-кастинг")],
            [KeyboardButton(text="📈 Мой прогресс"), KeyboardButton(text="❓ Справка")],
        ],
        resize_keyboard=True,
    )


@router.message(Command("menu"))
async def cmd_menu(m: Message):
    await m.answer("Меню открыто.", reply_markup=main_menu())


@router.message(Command("help"))
async def cmd_help(m: Message):
    await m.answer(
        "Команды:\n"
        "/start — начать/онбординг\n"
        "/menu — открыть меню\n"
        "/progress — мой прогресс\n"
        "/apply — Путь лидера (заявка)\n"
        "/coach_on — включить наставника\n"
        "/coach_off — выключить наставника\n"
        "/privacy — политика"
    )


@router.message(Command("privacy"))
async def cmd_privacy(m: Message):
    await m.answer(PRIVACY_TEXT)
