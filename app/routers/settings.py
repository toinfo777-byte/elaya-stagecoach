from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.menu import (
    BTN_SETTINGS, BTN_DELETE, BTN_MENU,
    settings_menu, main_menu,
)
from app.storage.repo import Repo, async_session_maker

router = Router(name="settings")


@router.message(F.text == BTN_SETTINGS)
async def open_settings(message: Message):
    await message.answer(
        "Настройки. Можешь удалить профиль или вернуться в меню.",
        reply_markup=settings_menu()
    )


@router.message(F.text == BTN_DELETE)
async def delete_profile(message: Message, state: FSMContext):
    await state.clear()
    async with async_session_maker() as session:
        repo = Repo(session)
        await repo.delete_user(message.from_user.id)
    await message.answer(
        "🗑 Профиль удалён. Можем начать заново — жми «Меню».",
        reply_markup=main_menu()
    )


@router.message(F.text == BTN_MENU)
async def back_to_menu_from_settings(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Готово! Открываю меню.", reply_markup=main_menu())
