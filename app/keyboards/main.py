# app/keyboards/main.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_kb() -> ReplyKeyboardMarkup:
    # Клавиатура показывается только в ЛС (см. роуты)
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🏋️ Тренировка дня"),
                KeyboardButton(text="📈 Мой прогресс"),
            ],
            [
                KeyboardButton(text="🎭 Мини-кастинг"),
                KeyboardButton(text="🧭 Путь лидера"),
            ],
            [
                KeyboardButton(text="💬 Помощь / FAQ"),
                KeyboardButton(text="⚙️ Настройки"),
            ],
            [
                KeyboardButton(text="🔐 Политика"),
                KeyboardButton(text="⭐ Расширенная версия"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=True,
    )
