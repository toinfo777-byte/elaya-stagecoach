from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MAIN_BTNS = [
    ["🎯 Тренировка дня", "🎭 Мини-кастинг"],
    ["📈 Мой прогресс", "⚙️ Настройки"],
    ["💬 Помощь", "⭐ Расширенная версия"],
]

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=txt) for txt in row] for row in MAIN_BTNS],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие…",
    )
