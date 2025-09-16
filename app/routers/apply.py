# app/routers/apply.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.states import ApplyStates
from app.routers.menu import BTN_APPLY, main_menu

router = Router(name="apply")

@router.message(StateFilter("*"), Command("apply"))
@router.message(StateFilter("*"), F.text == BTN_APPLY)
async def apply_start(m: Message, state: FSMContext):
    await state.set_state(ApplyStates.wait_text)
    await m.answer("Путь лидера: короткая заявка.\n\nНапишите, чего хотите достичь — одним сообщением.")

@router.message(ApplyStates.wait_text, ~F.text.startswith("/"))
async def apply_save(m: Message, state: FSMContext):
    text = (m.text or "").strip()
    # тут можешь сохранить в БД; я просто подтвержу
    await state.clear()
    await m.answer("Принято. Спасибо! Свяжемся по итогам. Возвращаю в меню.", reply_markup=main_menu())
