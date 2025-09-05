from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 Тренировка дня")],
            [KeyboardButton(text="📈 Мой прогресс")],
            [KeyboardButton(text="💬 Помощь"), KeyboardButton(text="🔐 Политика")],
            [KeyboardButton(text="🗑 Удалить профиль")],  # NEW
        ],
        resize_keyboard=True
    )
