# app/keyboards/inline.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def casting_skip_kb() -> InlineKeyboardMarkup:
    # синхронизировано с хендлером: F.data == "cast:skip_url"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data="cast:skip_url")]
        ]
    )
