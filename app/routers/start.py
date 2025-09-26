from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.filters.command import CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.reply import main_menu_kb

router = Router(name="start")

@router.message(StateFilter("*"), CommandStart(deep_link=True))
async def start_with_deeplink(msg: Message, command: CommandObject, state: FSMContext):
    payload = (command.args or "").strip().lower()

    # диплинки старого формата
    if payload.startswith("go_casting"):
        from app.routers.minicasting import start_minicasting
        await start_minicasting(msg, state)
        return

    if payload.startswith("go_training"):
        from app.routers.training import show_training_levels
        await show_training_levels(msg, state)
        return

    # по умолчанию — обычный старт
    await state.clear()
    await msg.answer("Привет! Я Элайя — тренер сцены. Помогу прокачать голос и уверенность.")
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())


@router.message(StateFilter("*"), CommandStart())
async def plain_start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Привет! Я Элайя — тренер сцены. Помогу прокачать голос и уверенность.")
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
