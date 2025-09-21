from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import BTN_APPLY

router = Router(name="apply")

async def open_apply(m: Message, source: str | None = None, post_id: str | None = None):
    # TODO: твоя бизнес-логика «Путь лидера»
    await m.answer("Путь лидера")

@router.message(Command("apply"))
async def cmd_apply(m: Message):
    await open_apply(m, source="/apply")

@router.message(F.text == BTN_APPLY)
async def btn_apply(m: Message):
    await open_apply(m, source="menu_button")
