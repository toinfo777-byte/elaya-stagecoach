from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.menu import (
    main_menu, small_menu,
    BTN_TO_MENU, BTN_TO_SETTINGS, BTN_WIPE,
)
from app.storage.repo import session_scope
from app.storage.models import User

router = Router(name="reply_shortcuts")


# 🏠 В меню — всегда доступно, очищаем состояние, чтобы ничего не перехватывало
@router.message(F.text == BTN_TO_MENU)
@router.message(Command("menu"))
async def to_menu(m: Message, state: FSMContext) -> None:
    await state.clear()
    await m.answer("Меню", reply_markup=main_menu())


# ⚙️ Настройки — тоже доступно в любом состоянии
@router.message(F.text == BTN_TO_SETTINGS)
@router.message(Command("settings"))
async def to_settings(m: Message, state: FSMContext) -> None:
    await state.clear()
    await m.answer("Настройки. Можешь удалить профиль или вернуться в меню.", reply_markup=small_menu())


# 🗑 Удалить профиль (и /wipe_me)
@router.message(F.text == BTN_WIPE)
@router.message(Command("wipe_me"))
async def wipe_profile(m: Message, state: FSMContext) -> None:
    await state.clear()
    with session_scope() as s:
        # важно: удаляем по tg_id, а не по внутреннему PK id
        s.query(User).filter(User.tg_id ==_
