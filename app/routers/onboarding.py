# app/routers/onboarding.py
from __future__ import annotations
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.routers.help import show_main_menu

router = Router(name="onboarding")

@router.message(CommandStart())
async def onboarding(m: Message):
    await show_main_menu(m)
