# app/routers/privacy.py
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.reply import main_menu_kb, BTN_POLICY

router = Router(name="privacy")

PRIVACY_TEXT = (
    "Политика конфиденциальности: мы бережно храним ваши данные и "
    "используем их только для работы бота.\n\n"
    "Подробнее: https://example.com/privacy"
)

# Глобально: работает из ЛЮБОГО состояния и выводит в меню
@router.message(StateFilter("*"), Command("privacy"))
@router.message(StateFilter("*"), F.text == BTN_POLICY)
async def show_privacy(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(PRIVACY_TEXT)
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
