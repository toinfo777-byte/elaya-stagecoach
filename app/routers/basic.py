from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="basic")

@router.message(Command("start"))
async def start_cmd(m: Message):
    await m.answer("Привет! Я на связи. Доступно: /ping, /hq")

@router.message(Command("ping"))
async def ping_cmd(m: Message):
    await m.answer("pong")
