from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def casting_skip_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data="cast:skip_url")]
        ]
    )
