from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import (
    main_menu,
    BTN_SETTINGS,
    BTN_WIPE,
)

from app.storage.repo import session_scope, delete_user_cascade
from app.storage.models import User

router = Router(name="settings")

# ===== Inline-клавиатуры =====

def _settings_kb() -> InlineKeyboardMarkup:
    """Мини-меню настроек — не дублируем прямое удаление профиля."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧹 Стереть профиль…", callback_data="wipe_confirm")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="settings_back")],
    ])

def _confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Да, удалить", callback_data="wipe_yes"),
        InlineKeyboardButton(text="Отмена", callback_data="wipe_no"),
    ]])

# ===== Handlers =====

# Открыть «Настройки»
@router.message(F.text == BTN_SETTINGS)
async def open_settings(m: Message):
    txt = (
        "⚙️ *Настройки*\n\n"
        "Здесь будут собираться пользовательские опции.\n"
        "Сейчас доступно:\n"
        "• Стереть профиль и данные\n"
        "• Вернуться в меню"
    )
    await m.answer(txt, reply_markup=_settings_kb(), parse_mode="Markdown")

# Кнопка «⬅️ В меню»
@router.callback_query(F.data == "settings_back")
async def settings_back(cb: CallbackQuery):
    await cb.message.answer("Готово. Вот меню:", reply_markup=main_menu())
    await cb.answer()

# Большая кнопка внизу «🗑 Удалить профиль» — сразу к подтверждению
@router.message(F.text == BTN_WIPE)
async def wipe_me_button(m: Message):
    await m.answer("Удалить профиль и все записи? Это действие необратимо.", reply_markup=_confirm_kb())

# Альтернативная команда
@router.message(Command("wipe_me"))
async def wipe_me_command(m: Message):
    await m.answer("Удалить профиль и все записи? Это действие необратимо.", reply_markup=_confirm_kb())

# Нажали «Стереть профиль…» из мини-меню — показать подтверждение
@router.callback_query(F.data == "wipe_confirm")
async def wipe_confirm(cb: CallbackQuery):
    await cb.message.answer("Удалить профиль и все записи? Это действие необратимо.", reply_markup=_confirm_kb())
    await cb.answer()

# Подтверждение/отмена удаления
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
