# app/ui/menu.py
from __future__ import annotations
from aiogram.types import (
    Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
)

MENU_TEXT = (
    "Команды и разделы: выбери нужное 🧭"
)

def build_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏋️‍♂️ Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
            [KeyboardButton(text="🎯 Мини-кастинг"), KeyboardButton(text="💬 Помощь / FAQ")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="🔒 Политика")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=True
    )

async def show_main_menu(target: Message | CallbackQuery) -> None:
    """
    Единственная точка показа главного меню.
    Принимает Message или CallbackQuery.
    Никаких вторичных 'Команды и разделы...' после этого вызывать не нужно.
    """
    msg = target if isinstance(target, Message) else target.message
    await msg.answer(MENU_TEXT, reply_markup=build_main_keyboard())
