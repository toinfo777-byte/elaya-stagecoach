from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.reply import main_menu_kb

router = Router(name="training")


@router.message(StateFilter("*"), Command("training"))
async def show_training_levels(
    msg: Message,
    state: FSMContext,
):
    # при необходимости можно чистить состояние
    # await state.clear()

    await msg.answer(
        "Привет! Я Элайя — тренер сцены.\n"
        "Помогу прокачать голос, дыхание, уверенность и выразительность."
    )
    await msg.answer(
        "Готово! Открываю меню.",
        reply_markup=main_menu_kb(),
    )
