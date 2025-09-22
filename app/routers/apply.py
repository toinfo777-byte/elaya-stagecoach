# app/routers/apply.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.menu import BTN_APPLY
from app.flows.casting_flow import start_casting_flow

router = Router(name="apply")


@router.message(Command("apply"), StateFilter(None))
@router.message(F.text == BTN_APPLY, StateFilter(None))
async def apply_entry(message: Message, state: FSMContext) -> None:
    """Алиас: «Путь лидера» ведёт в мини-кастинг."""
    await start_casting_flow(message, state)
