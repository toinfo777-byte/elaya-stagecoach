from __future__ import annotations

import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)

router = Router(name="panic")
log = logging.getLogger("panic")

def _diagnostic_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🏋️ Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
        [KeyboardButton(text="🎭 Мини-кастинг"),   KeyboardButton(text="🧭 Путь лидера")],
        [KeyboardButton(text="💬 Помощь / FAQ"),   KeyboardButton(text="⚙️ Настройки")],
        [KeyboardButton(text="🔐 Политика"),       KeyboardButton(text="⭐ Расширенная версия")],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)

@router.message(Command("ping"))
async def cmd_ping(m: Message):
    await m.answer("pong 🟢")

@router.message(Command("panicmenu"))
async def cmd_panicmenu(m: Message):
    await m.answer("Диагностическое меню:", reply_markup=_diagnostic_kb())

@router.message(Command("panicoff"))
async def cmd_panicoff(m: Message):
    await m.answer("Ок, клавиатуру убрал.", reply_markup=ReplyKeyboardRemove())

# Никаких обработчиков обычного текста здесь нет.
