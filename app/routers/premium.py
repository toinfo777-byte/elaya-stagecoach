from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.keyboards.menu import BTN_PREMIUM, main_menu
from app.storage.repo import session_scope, log_event
from app.storage.models import User

router = Router(name="premium")

class PremiumLead(StatesGroup):
    wait_contact = State()

def _lead_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐️ Оставить заявку", callback_data="premium:lead")],
        [InlineKeyboardButton(text="ℹ️ Подробнее", callback_data="premium:more")],
    ])

@router.message(Command("premium"))
@router.message(F.text == BTN_PREMIUM)
async def premium_entry(m: Message):
    text = (
        "⭐️ <b>Расширенная версия</b>\n\n"
        "Планируем: персональные планы, расширенная аналитика, кастомные треки.\n"
        "Оставьте заявку — мы свяжемся, когда откроем доступ."
    )
    await m.answer(text, reply_markup=main_menu())
    await m.answer("Интересно? Нажмите ниже:", reply_markup=_lead_kb())

@router.callback_query(F.data == "premium:more")
async def premium_more(cb: CallbackQuery):
    await cb.answer()
    await cb.message.answer(
        "В бете формируем список интересантов. Приоритет — активные пользователи и подробные заявки.",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == "premium:lead")
async def premium_lead_start(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(PremiumLead.wait_contact)
    await cb.message.answer(
        "Ок! Напишите контакт (телеграм @username, телефон, email) и коротко ожидания.\n"
        "Одним сообщением, до 300 символов. /cancel — отмена.",
        reply_markup=main_menu()
    )

@router.message(StateFilter(PremiumLead.wait_contact), ~F.text.startswith("/"))
async def premium_lead_save(m: Message, state: FSMContext):
    txt = (m.text or "").strip()
    if not txt:
        await m.answer("Пусто. Напишите контакт и ожидания одним сообщением.")
        return
    if len(txt) > 300:
        await m.answer(f"Слишком длинно ({len(txt)}). Сократите до 300 символов.")
        return

    try:
        with session_scope() as s:
            u = s.query(User).filter_by(tg_id=m.from_user.id).first()
            if u:
                log_event(s, u.id, "premium_interest", {"payload": txt})
                s.commit()
    except Exception:
        pass

    await state.clear()
    await m.answer("Спасибо! Заявка сохранена. Мы свяжемся при открытии доступа ✨", reply_markup=main_menu())

@router.message(StateFilter(PremiumLead.wait_contact), F.text == "/cancel")
async def premium_lead_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Отменено. Возвращаю в меню.", reply_markup=main_menu())
