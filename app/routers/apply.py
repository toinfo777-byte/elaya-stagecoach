# app/routers/apply.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.menu import BTN_APPLY

router = Router(name="apply")

# Мягкий импорт общего сценария кастинга
try:
    from app.flows.casting_flow import start_casting_flow
except Exception:
    start_casting_flow = None


@router.message(Command("apply"), StateFilter(None))
@router.message(F.text == BTN_APPLY, StateFilter(None))
async def apply_entry(message: Message, state: FSMContext) -> None:
    """Алиас: «Путь лидера» ведёт в мини-кастинг. 
    Если flow недоступен — используем фоллбек."""
    if start_casting_flow:
        return await start_casting_flow(message, state)
    await message.answer("Заявка временно недоступна. Попробуй позже 🙏")
