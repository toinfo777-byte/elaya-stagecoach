from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- Тексты кнопок (единый источник истины) ---
BTN_TRAINING_TEXT = "📚 Тренировка дня"
BTN_PROGRESS_TEXT = "📈 Мой прогресс"
BTN_HELP_TEXT = "💬 Помощь"
BTN_FEEDBACK_TEXT = "📝 Отзыв о тренировке"
BTN_POLICY_TEXT = "🔐 Политика"
BTN_PREMIUM_TEXT = "⭐️ Расширенная версия"

# --- Кнопки главного меню ---
BTN_TRAINING = KeyboardButton(text=BTN_TRAINING_TEXT)
BTN_PROGRESS = KeyboardButton(text=BTN_PROGRESS_TEXT)
BTN_HELP = KeyboardButton(text=BTN_HELP_TEXT)
BTN_FEEDBACK = KeyboardButton(text=BTN_FEEDBACK_TEXT)
BTN_POLICY = KeyboardButton(text=BTN_POLICY_TEXT)
BTN_PREMIUM = KeyboardButton(text=BTN_PREMIUM_TEXT)

# --- Главное меню тренера ---
MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [BTN_TRAINING],
        [BTN_PROGRESS, BTN_HELP],
        [BTN_FEEDBACK],
        [BTN_POLICY, BTN_PREMIUM],
    ],
    resize_keyboard=True,
)
