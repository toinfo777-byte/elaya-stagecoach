# app/routers/apply.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import main_menu, BTN_LEADER

router = Router(name="apply")


@router.message(F.text == BTN_LEADER)
@router.message(Command("apply"))
async def apply_entry(m: Message) -> None:
    await m.answer("Путь лидера — заявка. (Здесь будет форма/инструкция)", reply_markup=main_menu())


# ── Сверхприоритетный выход в меню ────────────────────────────────
@router.message(F.text.in_({"Меню", "/menu"}))
async def leave_to_menu(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Готово! Открываю меню.", reply_markup=main_menu())
