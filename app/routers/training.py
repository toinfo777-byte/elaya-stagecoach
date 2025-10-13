# app/routers/training.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from app.keyboards.reply import main_menu_kb, BTN_TRAINING

router = Router(name="training")

async def training_entry(m: Message):
    await m.answer(
        "Тренировка дня:\n\n• «Пауза 2 секунды»\n• «Ровный тембр»\n\n(пока демо-заглушка, запуск круга появится в следующем коммите)",
        reply_markup=main_menu_kb()
    )

# Совместимость со старым импортом
async def show_training_levels(m: Message):
    await training_entry(m)

@router.message(Command("training", "levels", "уровни"))
async def cmd_training(m: Message):
    await training_entry(m)

@router.message(F.text == BTN_TRAINING)
async def btn_training(m: Message):
    await training_entry(m)
