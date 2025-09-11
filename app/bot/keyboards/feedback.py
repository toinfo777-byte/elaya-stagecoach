# app/bot/keyboards/feedback.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def rating_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥", callback_data="rate:hot"),
            InlineKeyboardButton(text="👌", callback_data="rate:ok"),
            InlineKeyboardButton(text="😐", callback_data="rate:meh"),
        ],
        [InlineKeyboardButton(text="✍️ 1 фраза", callback_data="rate:text")]
    ])

def skip_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="rate:skip")]
    ])
