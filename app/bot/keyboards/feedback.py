# app/bot/keyboards/feedback.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def feedback_inline_kb() -> InlineKeyboardMarkup:
    # 🔥 / 👌 / 😐 + «1 фраза»
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥", callback_data="fb:rate:hot"),
            InlineKeyboardButton(text="👌", callback_data="fb:rate:ok"),
            InlineKeyboardButton(text="😐", callback_data="fb:rate:meh"),
        ],
        [
            InlineKeyboardButton(text="✍️ 1 фраза", callback_data="fb:phrase"),
        ],
    ])
