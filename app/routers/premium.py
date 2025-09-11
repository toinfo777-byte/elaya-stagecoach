from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User, Lead

router = Router(name="premium")

def premium_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оставить контакт", callback_data="lead_start")],
        [InlineKeyboardButton(text="📣 Что нового в канале", url="https://t.me/elaya_theatre")]
    ])

class LeadForm(StatesGroup):
    email = State()
    note = State()

# Вход в премиум (в любом состоянии + фаззи по тексту)
@router.message(StateFilter("*"), Command("premium"))
@router.message(StateFilter("*"), lambda m: isinstance(m.text, str) and "Расширен" in m.text)
async def premium_entry(m: Message):
    text = (
        "⭐ Расширенная версия (stub)\n\n"
        "Пакеты:\n"
        "• Персональный трек 4 недели\n"
        "• Мини-группа «Проба сцены»\n\n"
        "Нажми «Оставить контакт» — мы напишем с подробностями."
    )
    await m.answer(text, reply_markup=premium_kb())

@router.callback_query(F.data == "lead_start")
async def lead_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(LeadForm.email)
    await cb.message.answer("✉️ Введите email (необязательно). Если хотите пропустить — отправьте «-».")
    await cb.answer()

@router.message(LeadForm.email)
async def lead_email(m: Message, state: FSMContext):
    email = None if (m.text or "").strip() == "-" else (m.text or "").strip()
    await state.update_data(email=email)
    await state.set_state(LeadForm.note)
    await m.answer("Любой комментарий/предпочитаемый мессенджер — по желанию. Или отправьте «-».")

@router.message(LeadForm.note)
async def lead_note(m: Message, state: FSMContext):
    data = await state.get_data()
    note = None if (m.text or "").strip() == "-" else (m.text or "").strip()
    tg_contact = f"@{m.from_user.username}" if m.from_user.username else str(m.from_user.id)

    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            u = User(tg_id=m.from_user.id, username=m.from_user.username or "", name=m.from_user.full_name)
            s.add(u)
            s.flush()

        payload = []
        if data.get("email"):
            payload.append(f"email={data['email']}")
        if note:
            payload.append(f"note={note}")
        final_note = "; ".join(payload) if payload else None

        lead = Lead(user_id=u.id, channel="telegram", contact=tg_contact, note=final_note)
        s.add(lead)

    await state.clear()
    await m.answer("👍 Контакт записан. Спасибо! Мы свяжемся.", reply_markup=main_menu())
