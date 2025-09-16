from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from app.routers.menu import BTN_APPLY, main_menu

router = Router(name="apply")

class ApplyForm(StatesGroup):
    text = State()

async def apply_entry(m: Message, state: FSMContext):
    """
    Точка входа в «Путь лидера». Можно вызывать из шорткатов.
    """
    await m.answer("Путь лидера: короткая заявка.\nНапишите, чего хотите достичь — одним сообщением.", reply_markup=main_menu())
    await state.set_state(ApplyForm.text)

@router.message(Command("apply"))
async def apply_cmd(m: Message, state: FSMContext):
    await apply_entry(m, state)

@router.message(F.text == BTN_APPLY)
async def apply_btn(m: Message, state: FSMContext):
    await apply_entry(m, state)

@router.message(ApplyForm.text, ~F.text.startswith("/"))
async def apply_text(m: Message, state: FSMContext):
    # здесь можно сохранить в базу; пока просто подтверждаем
    await state.clear()
    await m.answer("Спасибо! Принял. Двигаемся дальше 💪", reply_markup=main_menu())

@router.message(ApplyForm.text, F.text.in_({"cancel", "/cancel"}))
async def apply_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Анкета отменена. Возвращаю в меню.", reply_markup=main_menu())
