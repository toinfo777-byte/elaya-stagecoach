# app/bot/ui/feedback.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message

# callback-data: "fb:hot" | "fb:ok" | "fb:meh" | "fb:phrase"
def build_feedback_kb() -> InlineKeyboardMarkup:
    row1 = [
        InlineKeyboardButton(text="🔥", callback_data="fb:hot"),
        InlineKeyboardButton(text="👌", callback_data="fb:ok"),
        InlineKeyboardButton(text="😐", callback_data="fb:meh"),
    ]
    row2 = [
        InlineKeyboardButton(text="✍ 1 фраза", callback_data="fb:phrase"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2])

async def send_feedback_prompt(target: Message) -> None:
    """
    Показывает универсальный блок «Как прошёл этюд? …» с нашей клавиатурой.
    Вызывайте из любого места: await send_feedback_prompt(message)
    """
    kb = build_feedback_kb()
    await target.answer(
        "Как прошёл этюд? Оцените или оставьте краткий отзыв:",
        reply_markup=kb
    )
