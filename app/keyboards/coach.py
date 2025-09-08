from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def timer_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🕒 60 сек", callback_data="coach_timer_60")]
    ])
