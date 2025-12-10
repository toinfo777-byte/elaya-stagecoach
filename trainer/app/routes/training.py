# trainer/app/routes/training.py
from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.main_menu import BTN_TRAINING
from .training_flow import start_training

router = Router()


@router.message(F.text == BTN_TRAINING)
async def handle_training_entry(message: Message, state: FSMContext) -> None:
    await start_training(message, state)
