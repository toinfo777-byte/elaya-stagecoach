# app/routers/apply.py
from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.config import settings
from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User
from app.services.leads import create_lead, LeadPayload

router = Router(name="apply")

INVITE_TEXT = (
    "«Путь лидера» — вейтлист на новую центральную ось.\n"
    "Оставьте короткую заявку — вернёмся с деталями."
)

def invite_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оставить заявку", callback_data="apply_start")]
        ]
    )

class ApplyFSM(StatesGroup):
    name = State()
    city_tz = State()
    contact = State()
    motivation = State()

# --- входные точки ---
@router.message(StateFilter("*"), F.text == "Путь лидера")
@router.message(StateFilter("*"), Command("apply"))
async def apply_entry(m: Message, state: FSMContext):
    await state.set_state(ApplyFSM.name)
    await m.answer("Как вас зовут? (имя/ник)")

@router.callback_query(StateFilter("*"), F.data == "apply_start")
async def apply_from_button(cb: CallbackQuery, state: FSMContext):
    await state.set_state(ApplyFSM.name)
    await cb.message.answer("Как вас зовут? (имя/ник)")
    await cb.answer()

# --- форма ---
@router.message(ApplyFSM.name, F.text.len() > 0)
async def step_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text.strip())
    await state.set_state(ApplyFSM.city_tz)
    await m.answer("Ваш город / часовой пояс? (например: Москва / Europe/Moscow)")

@router.message(ApplyFSM.city_tz, F.text.len() > 0)
async def step_city(m: Message, state: FSMContext):
    await state.update_data(city_tz=m.text.strip())
    await state.set_state(ApplyFSM.contact)
    prefill = f"@{m.from_user.username}" if m.from_user.username else ""
    hint = f"\nЕсли удобно, можно так: {prefill}" if prefill else ""
    await m.answer("Контакт для связи (телеграм @ / почта):" + hint)

@router.message(ApplyFSM.contact, F.text.len() > 0)
async def step_contact(m: Message, state: FSMContext):
    await state.update_data(contact=m.text.strip())
    await state.set_state(ApplyFSM.motivation)
    await m.answer("Коротко: мотивация (1–2 предложения).")

@router.message(ApplyFSM.motivation, F.text.len() > 0)
async def step_motivation(m: Message, state: FSMContext):
    d = await state.get_data()
    name = d.get("name") or m.from_user.full_name
    city_tz = d.get("city_tz", "")
    contact = d.get("contact", "")
    motivation = m.text.strip()

    # канал связи: грубая эвристика
    ch = "email" if ("@" in contact and " " not in contact and "." in contact) and not contact.startswith("@") else "telegram"
    note = f"name={name}; city_tz={city_tz}; motivation={motivation}"

    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            u = User(tg_id=m.from_user.id, username=m.from_user.username or "", name=m.from_user.full_name)
            s.add(u); s.flush()
        lead = create_lead(
            s, u.id,
            LeadPayload(channel=ch, contact=contact or (f"@{m.from_user.username}" if m.from_user.username else str(m.from_user.id))),
            # track и note — важное:
            # (передаём как именованные, чтобы не перепутать порядок)
        )
        # обновим track и note (если create_lead из старой версии без новых полей)
        lead.track = "leader"
        lead.note = note
        s.commit()

    # уведомление админам
    for admin_id in settings.admin_ids:
        try:
            src = "(без source)"
            with session_scope() as s2:
                u2 = s2.query(User).filter_by(tg_id=m.from_user.id).first()
                if u2 and getattr(u2, "source", None):
                    src = f"source={u2.source}"
            await m.bot.send_message(
                admin_id,
                f"Новая заявка «Путь лидера»\n"
                f"id={m.from_user.id} @{m.from_user.username or '-'}\n"
                f"{name}, {city_tz}\n"
                f"contact: {contact}\n"
                f"{src}\n"
                f"motivation: {motivation[:300]}"
            )
        except Exception:
            pass

    await state.clear()
    await m.answer("Заявка принята, вернёмся с деталями. Спасибо! 🙌", reply_markup=main_menu())

# --- спец-экран по deeplink ---
@router.message(StateFilter("*"), F.text.regexp(r"^/start(?:\s+leader_waitlist)?$"))
async def start_leader_invite(m: Message):
    # source сохранится в онбординге (users.source) — мы его уже не перетираем
    if "leader_waitlist" in (m.text or ""):
        await m.answer(INVITE_TEXT, reply_markup=invite_kb())
