# app/routers/feedback_demo.py
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.routers.feedback import kb as feedback_kb

router = Router(name="feedback_demo")

@router.message(Command("feedback_demo"))
async def feedback_demo(msg: Message):
    await msg.answer(
        "Как прошёл этюд? Оцените или оставьте короткий отзыв:",
        reply_markup=feedback_kb(),
    )
