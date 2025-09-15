# app/routers/feedback_demo.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.handlers.feedback import send_feedback_keyboard

router = Router(name="feedback_demo")

@router.message(Command("feedback_demo"))
async def feedback_demo(msg: Message):
    await send_feedback_keyboard(msg.bot, msg.chat.id)
