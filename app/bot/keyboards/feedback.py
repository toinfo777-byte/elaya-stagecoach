# app/bot/keyboards/feedback.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def feedback_inline_kb(prefix: str = "fb") -> InlineKeyboardMarkup:
    # callback_data:
    #   {prefix}:rate:hot | {prefix}:rate:ok | {prefix}:rate:meh | {prefix}:text
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥", callback_data=f"{prefix}:rate:hot"),
            InlineKeyboardButton(text="👌", callback_data=f"{prefix}:rate:ok"),
            InlineKeyboardButton(text="😐", callback_data=f"{prefix}:rate:meh"),
        ],
        [
            InlineKeyboardButton(text="✍️ 1 фраза", callback_data=f"{prefix}:text"),
        ],
    ])
