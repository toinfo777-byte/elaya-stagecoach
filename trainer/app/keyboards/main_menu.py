# trainer/app/keyboards/main_menu.py
from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Тексты кнопок
BTN_TRAINING = "🎭 Тренировка дня"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_HELP = "💬 Помощь"
BTN_PRO = "⭐ Расширенная версия"

# Главное меню тренера
MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_TRAINING)],
        [KeyboardButton(text=BTN_PROGRESS)],
        [KeyboardButton(text=BTN_HELP)],
        [KeyboardButton(text=BTN_PRO)],
    ],
    resize_keyboard=True,
)

# Небольшая совместимость, если где-то ещё будут старые имена
BTN_TRAINING_DAY = BTN_TRAINING
BTN_PRO_VERSION = BTN_PRO
