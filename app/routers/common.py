# app/routers/common.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router(name="common-guard")

# Блокируем слэш-команды внутри форм/анкеты
@router.message(
    any_state,
    Command(commands={"start", "menu", "training", "casting",
                      "apply", "progress", "privacy",
                      "help", "settings", "extended"})
)
async def block_commands_inside_forms(msg: Message, state: FSMContext):
    if await state.get_state() is not None:
        await msg.answer("Сейчас мы заполняем заявку. Чтобы выйти — жми «🏠 В меню».")
