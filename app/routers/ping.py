# app/routers/ping.py
from aiogram import Router, F
from aiogram.types import Message

router = Router(name="ping")

@router.message(F.text.lower().in_({"/ping", "ping"}))
async def ping(message: Message):
    await message.answer("pong")
