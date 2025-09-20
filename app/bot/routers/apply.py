from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.keyboards.menu import main_menu, BTN_APPLY

router = Router(name="apply")

_USER_APPS: dict[int, list[str]] = {}

class ApplySG(StatesGroup):
    wait_goal = State()

@router.message(Command("apply"))
@router.message(F.text == BTN_APPLY)
async def apply_entry(message: Message, state: FSMContext) -> None:
    await state.set_state(ApplySG.wait_goal)
    await message.answer(
        "Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — отправьте /cancel.",
        reply_markup=main_menu(),
    )

@router.message(Command("cancel"), ApplySG.wait_goal)
async def apply_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Отменил. Вернул в меню.", reply_markup=main_menu())

@router.message(ApplySG.wait_goal, F.text.len() > 0)
async def apply_save_goal(message: Message, state: FSMContext) -> None:
    _USER_APPS.setdefault(message.from_user.id, []).append(message.text[:200])
    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=main_menu())
