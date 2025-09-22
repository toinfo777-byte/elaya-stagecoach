# app/keyboards/menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- КОНСТАНТЫ КНОПОК ---
BTN_TRAINING = "🏋️ Тренировка дня"
BTN_APPLY = "🧭 Путь лидера"
BTN_POLICY = "🔐 Политика"
BTN_SETTINGS = "⚙️ Настройки"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_CASTING = "🎭 Мини-кастинг"
BTN_HELP = "💬 Помощь"
BTN_EXTENDED = "⭐ Расширенная версия"

BTN_MENU = "🏠 В меню"
BTN_DELETE = "🗑 Удалить профиль"

BTN_LEVEL_BEGINNER = "🟢 Новичок"
BTN_LEVEL_MEDIUM = "🟡 Средний"
BTN_LEVEL_PRO = "🔴 Про"

BTN_DONE = "✅ Выполнил(а)"
BTN_SKIP = "🎛 Пропустить"
BTN_SKIP_YES = "Да, пропустить"
BTN_SKIP_NO = "Отмена"


# --- МЕНЮ ---
def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_TRAINING), KeyboardButton(text=BTN_PROGRESS)],
            [KeyboardButton(text=BTN_APPLY), KeyboardButton(text=BTN_CASTING)],
            [KeyboardButton(text=BTN_POLICY), KeyboardButton(text=BTN_HELP)],
            [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_EXTENDED)],
        ],
        resize_keyboard=True
    )


def settings_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_MENU)],
            [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_DELETE)],
        ],
        resize_keyboard=True
    )
