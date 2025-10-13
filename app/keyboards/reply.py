# app/keyboards/reply.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BTN_TRAINING = "🏋️ Тренировка дня"
BTN_PROGRESS = "📈 Мой прогресс"
BTN_LEADER   = "🧭 «Путь лидера»"
BTN_PRIVACY  = "🔐 Политика"
BTN_SETTINGS = "⚙️ Настройки"
BTN_EXTENDED = "⭐️ «Расширенная версия» — позже"
BTN_HELP     = "💬 Помощь / FAQ"
BTN_MENU     = "🏠 В меню"
BTN_CASTING  = "🎭 Мини-кастинг"

def main_menu_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=BTN_TRAINING), KeyboardButton(text=BTN_PROGRESS)],
        [KeyboardButton(text=BTN_LEADER),   KeyboardButton(text=BTN_CASTING)],
        [KeyboardButton(text=BTN_PRIVACY),  KeyboardButton(text=BTN_SETTINGS)],
        [KeyboardButton(text=BTN_EXTENDED), KeyboardButton(text=BTN_HELP)],
    ]
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Команды и разделы: выбери нужное ⤵️"
    )
