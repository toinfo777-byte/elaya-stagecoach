# app/bot/keyboards/feedback.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def feedback_inline_kb(prefix: str = "fb") -> InlineKeyboardMarkup:
    """
    Инлайн-клава для универсальных отзывов.
    callback_data:
      fb:rate:hot | fb:rate:ok | fb:rate:meh
      fb:text     — попросить 1 фразу текста
    """
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

__all__ = ["feedback_inline_kb"]
