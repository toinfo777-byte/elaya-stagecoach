from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.routers.help import show_main_menu
from app.keyboards.reply import BTN_SETTINGS
# ВАЖНО: берём заглушку удаления из repo_extras, чтобы не тянуть БД-реализацию
from app.storage.repo_extras import delete_user  # async-заглушка удаления по tg_id

router = Router(name="settings")

SETTINGS_LOCK_KEY = "settings_shown"


def settings_inline_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 В меню", callback_data="settings:menu")
    kb.button(text="🗑 Удалить профиль", callback_data="settings:delete")
    kb.adjust(1)
    return kb.as_markup()


# Глобально + антидубль
@router.message(StateFilter("*"), Command("settings"))
@router.message(StateFilter("*"), F.text == BTN_SETTINGS)
async def open_settings(m: Message, state: FSMContext):
    data = await state.get_data()
    if data.get(SETTINGS_LOCK_KEY):
        return
    await state.update_data(**{SETTINGS_LOCK_KEY: True})
    await m.answer(
        "⚙️ Настройки. Можешь удалить профиль или вернуться в меню.",
        reply_markup=settings_inline_kb(),
    )


@router.callback_query(F.data == "settings:menu")
async def back_to_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    # показываем ровно то же меню, что и при /start
    await show_main_menu(cb)


@router.callback_query(F.data == "settings:delete")
async def delete_profile(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await delete_user(cb.from_user.id)  # заглушка — всегда «успех»
        text = "Готово. Профиль удалён."
    except Exception:
        text = "Не удалось удалить профиль. Попробуй позже."
    await cb.message.answer(text)
    await show_main_menu(cb)
