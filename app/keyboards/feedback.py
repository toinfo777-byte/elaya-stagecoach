from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def feedback_kb(ctx: str, ctx_id: str | None = None) -> InlineKeyboardMarkup:
    """ctx: 'training' | 'casting' | 'manual'"""
    tail = f"|{ctx_id}" if ctx_id else ""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔥", callback_data=f"fb_score|2|{ctx}{tail}"),
                InlineKeyboardButton(text="👌", callback_data=f"fb_score|1|{ctx}{tail}"),
                InlineKeyboardButton(text="😬", callback_data=f"fb_score|0|{ctx}{tail}"),
            ],
            [InlineKeyboardButton(text="✍️ 1 фраза", callback_data=f"fb_text|{ctx}{tail}")],
        ]
    )
