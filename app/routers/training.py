from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import BTN_TRAINING

router = Router(name="training")

# ЕДИНАЯ ТОЧКА ВХОДА (вызов из меню, командой или диплинком)
async def open_training(m: Message, source: str | None = None):
    # TODO: тут размести свою реальную логику тренировки.
    # Сейчас — минимальный маркер, чтобы было видно, что диплинк сработал.
    await m.answer("Тренировка дня")

@router.message(Command("training"))
async def cmd_training(m: Message):
    await open_training(m, source="/training")

@router.message(F.text == BTN_TRAINING)
async def btn_training(m: Message):
    await open_training(m, source="menu_button")
