# app/routers/onboarding.py
from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards.menu import main_menu
from app.storage.models import User
from app.storage.repo import session_scope

router = Router(name="onboarding")


@router.message(CommandStart(deep_link=False))
async def start_generic(m: Message) -> None:
    # создаём/обновляем пользователя
    with session_scope() as s:
        user = s.query(User).filter(User.tg_id == m.from_user.id).one_or_none()
        if user is None:
            user = User(
                tg_id=m.from_user.id,
                username=m.from_user.username or None,
                name=(m.from_user.first_name or "") + (" " + (m.from_user.last_name or "") if m.from_user.last_name else ""),
                tz=None, goal=None, exp_level=None, streak=0,
            )
            s.add(user)
        else:
            user.username = m.from_user.username or user.username

    await m.answer("Готово! Открываю меню.", reply_markup=main_menu())
