# app/routers/menu.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router(name="menu")

BTN_TRAIN = "🎯 Тренировка дня"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_APPLY = "🧭 Путь лидера"
BTN_CASTING = "🎭 Мини-кастинг"
BTN_HELP = "💬 Помощь"
BTN_POLICY = "🔐 Политика"

def main_menu() -> ReplyKeyboardMarkup:
    # persistency у телеграма для reply-клавы глобально не гарантируется,
    # поэтому присылаем ее почаще.
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_TRAIN), KeyboardButton(text=BTN_PROGRESS)],
            [KeyboardButton(text=BTN_APPLY), KeyboardButton(text=BTN_CASTING)],
            [KeyboardButton(text=BTN_POLICY), KeyboardButton(text=BTN_HELP)],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

@router.message(Command("menu"))
async def open_menu(m: Message):
    await m.answer("Меню", reply_markup=main_menu())

# Экспортируем кнопки для других модулей
__all__ = [
    "router",
    "BTN_TRAIN", "BTN_PROGRESS", "BTN_APPLY", "BTN_CASTING", "BTN_HELP", "BTN_POLICY",
    "main_menu",
]
