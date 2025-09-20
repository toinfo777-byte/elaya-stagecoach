from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
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
    await message.answer(
        "Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — отправьте /cancel."
    )


@router.message(ApplySG.wait_goal)
async def apply_save(message: Message, state: FSMContext) -> None:
    # тут сохраняем заявку в БД/память по желанию
    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=main_menu())
