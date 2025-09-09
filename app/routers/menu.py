from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.menu import main_menu as _main_menu

router = Router(name="menu")


@router.message(Command("menu"))
async def menu_cmd(m: Message, state: FSMContext):
    # если юзер в каком-то процессе (анкета/тренировка и т.п.) — освобождаем
    try:
        await state.clear()
    except Exception:
        pass
    await m.answer("Готово. Вот меню:", reply_markup=_main_menu())


# На всякий случай кнопка «Меню» из клавиатуры (текст может слегка отличаться)
@router.message(F.text.casefold() == "меню")
async def menu_button(m: Message, state: FSMContext):
    try:
        await state.clear()
    except Exception:
        pass
    await m.answer("Готово. Вот меню:", reply_markup=_main_menu())
