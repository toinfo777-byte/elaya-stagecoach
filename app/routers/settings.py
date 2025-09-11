# app/routers/settings.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import main_menu
from app.storage.repo import session_scope, delete_user_cascade
from app.storage.models import User

router = Router(name="settings")

def _settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить профиль", callback_data="wipe_confirm")],
    ])

def _confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, удалить", callback_data="wipe_yes"),
            InlineKeyboardButton(text="Отмена", callback_data="wipe_no"),
        ]
    ])

# Открыть настройки: и по кнопке, и по /settings
@router.message(Command("settings"))
@router.message(F.text == "⚙️ Настройки")
async def open_settings(m: Message):
    await m.answer(
        "⚙️ Настройки профиля:\n\n"
        "• Здесь вы можете удалить профиль и все записи (онбординг начнётся заново).\n\n"
        "В бете других настроек нет.",
        reply_markup=_settings_kb(),
    )

# Прямая команда — быстрый запрос подтверждения
@router.message(Command("wipe_me"))
async def wipe_me_command(m: Message):
    await m.answer("Удалить профиль и все записи? Это действие необратимо.", reply_markup=_confirm_kb())

@router.callback_query(F.data == "wipe_confirm")
async def wipe_confirm(cb: CallbackQuery):
    await cb.message.answer("Удалить профиль и все записи? Это действие необратимо.", reply_markup=_confirm_kb())
    await cb.answer()

@router.callback_query(F.data.in_({"wipe_no", "wipe_yes"}))
async def wipe_actions(cb: CallbackQuery, state: FSMContext):
    if cb.data == "wipe_no":
        await cb.message.answer("Ок, ничего не удалял.", reply_markup=main_menu())
        await cb.answer()
        return

    # wipe_yes
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=cb.from_user.id).first()
        if u:
            delete_user_cascade(s, u.id)

    await state.clear()
    await cb.message.answer("Готово. Профиль удалён. /start — заново пройти онбординг.", reply_markup=main_menu())
    await cb.answer()
