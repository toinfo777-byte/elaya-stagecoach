from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import BTN_TRAINING

router = Router(name="training")

# Единая точка входа
async def open_training(m: Message, source: str | None = None, post_id: str | None = None):
    # TODO: твоя бизнес-логика; post_id — из диплинка
    await m.answer("Тренировка дня")

@router.message(Command("training"))
async def cmd_training(m: Message):
    await open_training(m, source="/training")

@router.message(F.text == BTN_TRAINING)
async def btn_training(m: Message):
    await open_training(m, source="menu_button")
