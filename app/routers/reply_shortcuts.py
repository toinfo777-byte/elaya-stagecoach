from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import (
    main_menu, small_menu,
    BTN_TO_MENU, BTN_TO_SETTINGS, BTN_WIPE,
)
from app.storage.repo import session_scope
from app.storage.models import User

router = Router(name="reply_shortcuts")

# 🏠 В меню
@router.message(F.text == BTN_TO_MENU)
async def to_menu(m: Message):
    await m.answer("Меню", reply_markup=main_menu())

# ⚙️ Настройки
@router.message(F.text == BTN_TO_SETTINGS)
async def to_settings(m: Message):
    await m.answer(
        "Настройки. Можешь удалить профиль или вернуться в меню.",
        reply_markup=small_menu(),
    )

# 🗑 Удалить профиль (и /wipe_me)
@router.message(F.text == BTN_WIPE)
@router.message(Command("wipe_me"))
async def wipe_profile(m: Message):
    # ВАЖНО: удаляем по tg_id, а не по внутреннему users.id
    with session_scope() as s:
        s.query(User).filter(User.tg_id == m.from_user.id).delete(synchronize_session=False)
    await m.answer("Ок, всё сбросил. Открываю меню.", reply_markup=main_menu())
