# app/routers/apply.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import BTN_APPLY
from app.routers.casting import start_casting_flow  # 👈 алиас на кастинг

router = Router(name="apply")

@router.message(Command("apply"), StateFilter(None))
@router.message(F.text == BTN_APPLY, StateFilter(None))
async def apply_alias(message: Message, state: FSMContext) -> None:
    """До выделенного сценария «Путь лидера» = мини-кастинг."""
    await start_casting_flow(message, state)
