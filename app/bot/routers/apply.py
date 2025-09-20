from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.bot.keyboards.menu import main_menu_kb

router = Router(name="apply")


class ApplySG(StatesGroup):
    waiting_goal = State()


@router.message(Command("apply"))
@router.message(F.text == "🧭 Путь лидера")
async def apply_entry(message: Message, state: FSMContext) -> None:
    text = (
        "Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — отправьте /cancel."
    )
    await state.set_state(ApplySG.waiting_goal)
    await message.answer(text)


@router.message(Command("cancel"))
async def apply_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Ок, вернулись в главное меню.", reply_markup=main_menu_kb())


@router.message(ApplySG.waiting_goal, F.text.len() <= 200)
async def apply_save(message: Message, state: FSMContext) -> None:
    # Тут можно сохранить в вашу БД/репозиторий. Пока просто кладём в FSM (как пример).
    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=main_menu_kb())


@router.message(ApplySG.waiting_goal)
async def apply_too_long(message: Message) -> None:
    await message.answer("Слишком длинно 🙈 Отправьте цель одной короткой фразой (до 200 символов) или /cancel.")
