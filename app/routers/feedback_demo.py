# app/routers/feedback_demo.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.handlers.feedback import make_feedback_kb

router = Router(name="feedback_demo")

@router.message(Command("feedback_demo"))
async def show_feedback_kb(msg: Message):
    await msg.answer(
        "Как прошёл этюд? Оцените или оставьте короткий отзыв:",
        reply_markup=make_feedback_kb(),
    )
