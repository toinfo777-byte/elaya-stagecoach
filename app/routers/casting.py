# app/routers/casting.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_CASTING

router = Router(name="casting")


@router.message(F.text == BTN_CASTING)
@router.message(Command("casting"))
async def casting_entry(m: Message) -> None:
    await m.answer("Мини-кастинг", reply_markup=main_menu())


CASTING_START_RE = r"^/start(?:@\w+)?\s+go_casting_"

@router.message(CommandStart(deep_link=True), F.text.regexp(CASTING_START_RE))
async def start_from_casting_deeplink(m: Message) -> None:
    await casting_entry(m)
