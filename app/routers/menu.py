from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext  # NEW

from app.keyboards.menu import main_menu
from app.texts.strings import HELP
from app.routers.system import PRIVACY_TEXT, WipeFlow, _wipe_kb  # NEW: берём логику из system.py

router = Router(name="menu")


@router.message(Command("menu"))
async def menu_cmd(msg: Message):
    await msg.answer("Меню:", reply_markup=main_menu())


# /help и кнопка «Помощь»
@router.message(Command("help"))
@router.message(F.text == "💬 Помощь")
async def help_msg(msg: Message):
    await msg.answer(HELP, reply_markup=main_menu())


# Политика (кнопка и любые тексты где встречается «политик»)
@router.message(F.text.in_({"🔐 Политика", "Политика"}))
@router.message(lambda m: isinstance(m.text, str) and "политик" in m.text.lower())
async def privacy_msg(msg: Message):
    await msg.answer(PRIVACY_TEXT, reply_markup=main_menu())


# 🔥 Кнопка «Удалить профиль» — запускаем тот же flow, что у /wipe_me
@router.message(F.text.in_({"🗑 Удалить профиль", "Удалить профиль"}))
async def delete_profile_btn(msg: Message, state: FSMContext):
    await state.set_state(WipeFlow.confirm)
    await msg.answer(
        "⚠️ Вы собираетесь удалить профиль и все записи. Действие необратимо. Подтвердить?",
        reply_markup=_wipe_kb()
    )
