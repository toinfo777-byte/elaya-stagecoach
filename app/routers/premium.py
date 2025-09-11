# app/routers/premium.py
from __future__ import annotations

import re
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User, Lead

router = Router(name="premium")

# ---------- UI ----------

def premium_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оставить контакт", callback_data="lead_start")],
            [InlineKeyboardButton(text="📣 Что нового в канале", url="https://t.me/elaya_theatre")],
        ]
    )

# ---------- FSM ----------

class LeadForm(StatesGroup):
    email = State()
    note = State()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# ---------- Handlers ----------

# Кнопка и команда — работают в любом состоянии (в т.ч. во время анкеты)
@router.message(StateFilter("*"), F.text == "⭐ Расширенная версия")
@router.message(StateFilter("*"), Command("premium"))
async def premium_entry(m: Message):
    text = (
        "⭐ *Расширенная версия*\n\n"
        "Пакеты:\n"
        "• Персональный трек 4 недели\n"
        "• Мини-группа «Проба сцены»\n\n"
        "Нажми «Оставить контакт» — мы напишем с подробностями."
    )
    await m.answer(text, reply_markup=premium_kb(), parse_mode="Markdown")


@router.callback_query(StateFilter("*"), F.data == "lead_start")
async def lead_start(cb: CallbackQuery, state: FSMContext):
    await state.set_state(LeadForm.email)
    await cb.message.answer("✉️ Введите e-mail (необязательно). Если хотите пропустить — отправьте «-».")
    await cb.answer()


@router.message(LeadForm.email)
async def lead_email(m: Message, state: FSMContext):
    raw = (m.text or "").strip()
    email: str | None
    if raw == "-":
        email = None
    else:
        email = raw if EMAIL_RE.match(raw) else None
        if raw and not email:
            await m.answer("Похоже, формат e-mail некорректен. Введите другой или отправьте «-» чтобы пропустить.")
            return

    await state.update_data(email=email)
    await state.set_state(LeadForm.note)
    await m.answer(
        "Любой комментарий/предпочитаемый мессенджер (телеграм @, телефон и т.п.) — по желанию. "
        "Или отправьте «-».",
    )


@router.message(LeadForm.note)
async def lead_note(m: Message, state: FSMContext):
    data = await state.get_data()
    note_text = (m.text or "").strip()
    note = None if note_text == "-" else note_text[:500]  # ограничим длину

    # Контакт по умолчанию из Telegram
    tg_contact = f"@{m.from_user.username}" if m.from_user.username else str(m.from_user.id)

    with session_scope() as s:
        # user может отсутствовать, создадим минимально
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            u = User(tg_id=m.from_user.id, username=m.from_user.username or "", name=m.from_user.full_name)
            s.add(u)
            s.flush()

        parts: list[str] = []
        if data.get("email"):
            parts.append(f"email={data['email']}")
        if note:
            parts.append(f"note={note}")
        final_note = "; ".join(parts) if parts else None

        lead = Lead(
            user_id=u.id,
            channel="telegram",
            contact=tg_contact,
            note=final_note,
        )
        s.add(lead)
        # session_scope() коммитит самостоятельно по выходу

    await state.clear()
    await m.answer("👍 Контакт записан. Спасибо! Мы свяжемся.", reply_markup=main_menu())
