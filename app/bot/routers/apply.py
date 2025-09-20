from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_APPLY

router = Router(name="apply")

class ApplySG(StatesGroup):
    wait_goal = State()

@router.message(Command("apply"))
@router.message(F.text == BTN_APPLY)
async def apply_entry(message: Message, state: FSMContext) -> None:
    await state.set_state(ApplySG.wait_goal)
    text = (
        "Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — отправьте /cancel."
    )
    await message.answer(text, reply_markup=main_menu())

@router.message(ApplySG.wait_goal, ~F.text.startswith("/"))
async def apply_save_goal(message: Message, state: FSMContext) -> None:
    goal = (message.text or "").strip()[:200]
    # здесь можно сохранить в БД; сейчас просто подтверждаем
    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=main_menu())
