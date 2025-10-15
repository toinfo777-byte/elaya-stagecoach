# app/routers/healthcheck.py
from __future__ import annotations
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.build import BUILD_MARK
from app.health import uptime_seconds

router = Router()


@router.message(Command("health"))
async def cmd_health(message: Message):
    await message.answer(
        "ok ✅\n"
        f"<b>build</b>: {BUILD_MARK}\n"
        f"<b>uptime</b>: {uptime_seconds()}s"
    )
