from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# Экспортируемый роутер (именно 'router', чтобы импорт "from ... import router" работал)
router = Router(name="menu")

# ===== Константы подписей кнопок (единая точка правды) =====
BTN_TRAIN      = "🎯 Тренировка дня"
BTN_PROGRESS   = "📈 Мой прогресс"
BTN_CASTING    = "🎭 Мини-кастинг"

# «Путь лидера» — базовое имя:
BTN_LEADER     = "🧭 Путь лидера"
# Алиас для совместимости со старыми импортами:
BTN_APPLY      = BTN_LEADER

BTN_POLICY     = "🔐 Политика"
BTN_HELP       = "💬 Помощь"
BTN_SETTINGS   = "⚙️ Настройки"
BTN_PREMIUM    = "⭐ Расширенная версия"
BTN_DELETE     = "🗑 Удалить профиль"
BTN_MENU       = "Меню"

__all__ = [
    "router",
    "BTN_TRAIN", "BTN_PROGRESS", "BTN_CASTING",
    "BTN_LEADER", "BTN_APPLY",
    "BTN_POLICY", "BTN_HELP", "BTN_SETTINGS", "BTN_PREMIUM", "BTN_DELETE", "BTN_MENU",
    "main_menu",
]

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

# ===== Фолбэк на любой обычный текст вне состояний — вернуть в меню =====
@router.message(StateFilter(None), F.text)
async def any_text_to_menu(m: Message):
    if m.text and m.text.startswith("/"):  # команды ловят другие роутеры
        return
    await m.answer("Готово. Вот меню:", reply_markup=main_menu())
