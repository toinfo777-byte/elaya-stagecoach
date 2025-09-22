# app/routers/start.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.menu import main_menu
from app.routers.training import training_entry  # только для показа уровней тренировки

# мягкий импорт общего сценария кастинга из flows (без циклических импортов)
try:
    from app.flows.casting_flow import start_casting_flow
except Exception:
    start_casting_flow = None  # фоллбек, чтобы сервис не падал при импорт-ошибке

router = Router(name="start")


@router.message(CommandStart(deep_link=True))
async def start_with_deeplink(message: Message, command: CommandObject, state: FSMContext):
    """Обработка /start с payload: go_training*, go_casting*."""
    await state.clear()
    payload = (command.args or "").strip().lower() if command else ""

    if payload.startswith("go_training"):
        return await training_entry(message)

    if payload.startswith("go_casting"):
        if start_casting_flow:
            return await start_casting_flow(message, state)
        # мягкий фоллбек, если вдруг сценарий недоступен
        return await message.answer(
            "Заявка временно недоступна. Попробуй позже 🙏",
            reply_markup=main_menu(),
        )

    # дефолт — просто открыть меню
    await message.answer("Готово! Открываю меню.", reply_markup=main_menu())


@router.message(CommandStart())
async def start_plain(message: Message, state: FSMContext):
    """Обычный /start без payload — приветствие + меню."""
    await state.clear()
    await message.answer(
        "Привет! Я Элайя — тренер сцены. Помогу прокачать голос и уверенность.",
        reply_markup=main_menu(),
    )
