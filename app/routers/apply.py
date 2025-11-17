from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router(name="apply-router")

# Текст кнопки для подачи заявки (Путь лидера).
# Важно: держать в синхронизации с текстом кнопки в клавиатуре,
# если она есть.
BTN_APPLY = "🧭 Путь лидера"

# Мягкий импорт общего сценария кастинга (без циклических импортов)
try:
    from app.flows.casting_flow import start_casting_flow
except Exception:
    start_casting_flow = None


@router.message(Command("apply"), StateFilter(None))
@router.message(F.text == BTN_APPLY, StateFilter(None))
async def apply_entry(message: Message, state: FSMContext) -> None:
    """
    Вход в мини-кастинг ("Путь лидера").
    Если общий flow недоступен — выводим мягкий фоллбек.
    """
    if start_casting_flow:
        return await start_casting_flow(message, state)

    await message.answer("Заявка временно недоступна. Попробуй позже 🙏")
