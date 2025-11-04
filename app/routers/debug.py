from aiogram import Router, F
from aiogram.types import Message

router = Router(name="debug")

# Быстрый пинг для теста маршрутизации
@router.message(F.text == "ping")
async def ping(msg: Message):
    await msg.answer("pong")
