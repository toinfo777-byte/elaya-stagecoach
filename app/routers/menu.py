# app/routers/menu.py
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router(name="menu")

BTN_TRAIN     = "🏅 Тренировка дня"
BTN_PROGRESS  = "📈 Мой прогресс"
BTN_APPLY     = "🧭 Путь лидера"
BTN_CASTING   = "🎭 Мини-кастинг"
BTN_POLICY    = "🔐 Политика"
BTN_HELP      = "💬 Помощь"

def main_menu() -> ReplyKeyboardMarkup:
    # Единый порядок всегда
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_TRAIN), KeyboardButton(text=BTN_PROGRESS)],
            [KeyboardButton(text=BTN_APPLY), KeyboardButton(text=BTN_CASTING)],
            [KeyboardButton(text=BTN_POLICY), KeyboardButton(text=BTN_HELP)],
        ],
        resize_keyboard=True
    )

@router.message(Command("menu"))
async def open_menu(m: Message):
    await m.answer("Меню", reply_markup=main_menu())
