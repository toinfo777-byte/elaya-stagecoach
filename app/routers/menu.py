from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# Экспортируемый роутер — ИМЕННО ТАК, чтобы main смог: from app.routers.menu import router
router = Router(name="menu")

# ===== Константы подписей кнопок (единая точка правды) =====
BTN_TRAIN      = "🎯 Тренировка дня"
BTN_PROGRESS   = "📈 Мой прогресс"
BTN_CASTING    = "🎭 Мини-кастинг"
BTN_LEADER     = "🧭 Путь лидера"
BTN_POLICY     = "🔐 Политика"
BTN_HELP       = "💬 Помощь"
BTN_SETTINGS   = "⚙️ Настройки"
BTN_PREMIUM    = "⭐ Расширенная версия"
BTN_DELETE     = "🗑 Удалить профиль"
BTN_MENU       = "Меню"

# ===== Клавиатура главного меню =====
def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_TRAIN),   KeyboardButton(text=BTN_PROGRESS)],
            [KeyboardButton(text=BTN_LEADER),  KeyboardButton(text=BTN_CASTING)],
            [KeyboardButton(text=BTN_POLICY),  KeyboardButton(text=BTN_HELP)],
            [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_PREMIUM)],
            [KeyboardButton(text=BTN_DELETE)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню…",
    )

# ===== Открыть меню (/menu или кнопка «Меню») =====
@router.message(Command("menu"))
@router.message(F.text == BTN_MENU)
async def open_menu(m: Message):
    await m.answer("Меню:", reply_markup=main_menu())

# ===== Фолбэк на непонятный текст в «ничейном» состоянии — вернуть в меню =====
@router.message(StateFilter(None), F.text)
async def any_text_to_menu(m: Message):
    # Не перехватываем команды: их поймают другие роутеры по Command(...)
    if m.text and m.text.startswith("/"):
        return
    await m.answer("Готово. Вот меню:", reply_markup=main_menu())
