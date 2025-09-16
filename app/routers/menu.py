from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import StateFilter

# Тексты кнопок (используются во всех роутерах)
BTN_TRAIN     = "🎯 Тренировка дня"
BTN_PROGRESS  = "📈 Мой прогресс"
BTN_APPLY     = "🧭 Путь лидера"
BTN_CASTING   = "🎭 Мини-кастинг"
BTN_PRIVACY   = "🔐 Политика"
BTN_HELP      = "💬 Помощь"
BTN_SETTINGS  = "⚙️ Настройки"
BTN_PREMIUM   = "⭐️ Расширенная версия"
BTN_DELETE    = "🧹 Удалить профиль"

def main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=BTN_TRAIN),    KeyboardButton(text=BTN_PROGRESS)],
        [KeyboardButton(text=BTN_APPLY),    KeyboardButton(text=BTN_CASTING)],
        [KeyboardButton(text=BTN_PRIVACY),  KeyboardButton(text=BTN_HELP)],
        [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_PREMIUM)],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

router = Router(name="menu")

@router.message(StateFilter("*"), F.text.in_(
    ["/menu", "Меню", "меню"]
))
async def open_menu(m: Message):
    await m.answer("Выберите пункт меню…", reply_markup=main_menu())
