# app/routers/panic.py
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

# —————— вспомогательная клавиатура на 8 кнопок (диагностика) ——————
def _diagnostic_menu_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🏋️ Тренировка дня"), KeyboardButton(text="📈 Мой прогресс")],
        [KeyboardButton(text="🎭 Мини-кастинг"),   KeyboardButton(text="🧭 Путь лидера")],
        [KeyboardButton(text="💬 Помощь / FAQ"),   KeyboardButton(text="⚙️ Настройки")],
        [KeyboardButton(text="🔐 Политика"),       KeyboardButton(text="⭐ Расширенная версия")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Выбери раздел…",
    )

# —————— команды диагностики ——————
@router.message(Command("ping"))
async def cmd_ping(m: Message):
    await m.answer("pong 🟢")

@router.message(Command("panicmenu"))
async def cmd_panicmenu(m: Message):
    # показываем диагностическую reply-клавиатуру, НИЧЕГО не перехватывая
    await m.answer("✅ Диагностическая клавиатура включена.", reply_markup=_diagnostic_menu_kb())

@router.message(Command("panicoff"))
async def cmd_panicoff(m: Message):
    await m.answer("✅ Диагностическая клавиатура скрыта.", reply_markup=ReplyKeyboardRemove())

# ВАЖНО:
# — здесь НЕТ catch-all обработчиков типа @router.message() или фильтров на обычный текст
# — клавиатура просто отправляется; обработка нажатий уходит в боевые роутеры
