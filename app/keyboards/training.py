from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def levels_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Новичок", callback_data="training:level:beginner")],
        [InlineKeyboardButton(text="🟡 Средний",  callback_data="training:level:medium")],
        [InlineKeyboardButton(text="🔴 Про",     callback_data="training:level:pro")],
    ])

def actions_kb(level: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Выполнил(а)", callback_data=f"training:done:{level}"),
            InlineKeyboardButton(text="⏭ Пропустить",  callback_data=f"training:skip:{level}")
        ]
    ])

def skip_confirm_kb(level: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, пропустить", callback_data=f"training:skip-confirm:{level}"),
            InlineKeyboardButton(text="Отмена",          callback_data=f"training:skip-cancel:{level}"),
        ]
    ])
