# app/flows/casting_flow.py
from __future__ import annotations

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message


class ApplyForm(StatesGroup):
    """Единая FSM для мини-кастинга и «Пути лидера»."""
    name = State()
    age = State()
    city = State()
    experience = State()
    contact = State()
    portfolio = State()


async def start_casting_flow(message: Message, state: FSMContext) -> None:
    """
    Общая точка входа в анкету.
    Сбрасывает состояние, ставит первый шаг и задаёт вопрос.
    """
    await state.clear()
    await state.set_state(ApplyForm.name)
    await message.answer("Как тебя зовут?\n<i>Имя и фамилия</i>")
