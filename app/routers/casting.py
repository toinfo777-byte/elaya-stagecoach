from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import BTN_CASTING

router = Router(name="casting")

async def open_casting(m: Message, source: str | None = None, post_id: str | None = None):
    # TODO: твоя бизнес-логика; post_id — из диплинка
    await m.answer("Мини-кастинг")

@router.message(Command("casting"))
async def cmd_casting(m: Message):
    await open_casting(m, source="/casting")

@router.message(F.text == BTN_CASTING)
async def btn_casting(m: Message):
    await open_casting(m, source="menu_button")
