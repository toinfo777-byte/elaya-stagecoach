# app/routers/apply.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.routers.menu import main_menu

router = Router(name="apply")

async def apply_entry(m: Message, state: FSMContext):
    await state.clear()
    await m.answer(
        "🧭 Путь лидера: короткая заявка.\n\nНапишите, чего хотите достичь — одним сообщением.",
        reply_markup=main_menu(),
    )

@router.message(Command("apply"))
async def apply_cmd(m: Message, state: FSMContext):
    await apply_entry(m, state)

@router.message(StateFilter("*"), F.text == "🧭 Путь лидера")
async def apply_btn(m: Message, state: FSMContext):
    await apply_entry(m, state)
