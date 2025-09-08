# app/routers/apply.py
from __future__ import annotations

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.config import settings
from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User, Lead

router = Router(name="apply")


# ---------- helpers ----------
def _admin_ids_set() -> set[int]:
    """Безопасно читаем settings.admin_ids (list|set|tuple|str '1,2,3')."""
    try:
        ids = settings.admin_ids
        if isinstance(ids, (set, list, tuple)):
            return {int(x) for x in ids}
        if isinstance(ids, str):
            parts = ids.replace(";", ",").split(",")
            return {int(x.strip()) for x in parts if x.strip()}
    except Exception:
        pass
    return set()


def _invite_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оставить заявку", callback_data="apply_start")]
        ]
    )


# ---------- FSM ----------
class ApplyFlow(StatesGroup):
    name = State()
    city_tz = State()
    contact = State()
    motivation = State()


# ---------- deep-link: /start leader_waitlist ----------
@router.message(Command("start"), F.text.func(lambda t: isinstance(t, str) and "leader_waitlist" in t))
async def start_leader_waitlist(m: Message):
    # при старте через deep link — опционально сохраним источник
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if u and not getattr(u, "source", None):
            u.source = "leader_waitlist"

    text = (
        "🌟 «Путь лидера Элайи»\n\n"
        "Образовательная программа для воспитания руководителей авангарда смыслов.\n"
        "Готовы присоединиться к вейтлисту? Нажмите кнопку ниже и заполните короткую форму."
    )
    await m.answer(text, reply_markup=_invite_kb())


# ---------- entry points ----------
@router.message(Command("apply"))
@router.message(F.text == "Путь лидера")
async def apply_entry(m: Message, state: FSMContext):
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer("Сначала пройдите /start.", reply_markup=main_menu())
            return

        # если уже есть заявка — сообщаем
        exists = s.query(Lead).filter_by(user_id=u.id, track="leader").first()
        if exists:
            await m.answer(
                "Ваша заявка в трек «Лидер» уже получена ✅\n"
                "Мы свяжемся с вами по указанным контактам. "
                "Статус виден в «📈 Мой прогресс».",
                reply_markup=main_menu(),
            )
            return

    await state.set_state(ApplyFlow.name)
    suggested = " ".join(filter(None, [m.from_user.first_name, m.from_user.last_name]))
    suggested = suggested or (f"@{m.from_user.username}" if m.from_user.username else "")
    prompt = "Введите ваше имя (как к вам обращаться)"
    if suggested:
        prompt += f"\n\nНапример: *{suggested}*"
    await m.answer(prompt)


@router.callback_query(F.data == "apply_start")
async def apply_start_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.set_state(ApplyFlow.name)
    suggested = " ".join(filter(None, [cb.from_user.first_name, cb.from_user.last_name]))
    suggested = suggested or (f"@{cb.from_user.username}" if cb.from_user.username else "")
    prompt = "Введите ваше имя (как к вам обращаться)"
    if suggested:
        prompt += f"\n\nНапример: *{suggested}*"
    await cb.message.answer(prompt)


# ---------- steps ----------
@router.message(ApplyFlow.name)
async def step_name(m: Message, state: FSMContext):
    name = (m.text or "").strip()
    if not name:
        await m.answer("Пожалуйста, напишите имя текстом.")
        return
    await state.update_data(name=name)
    await state.set_state(ApplyFlow.city_tz)
    await m.answer("Ваш город и часовой пояс (например: «Санкт-Петербург, GMT+3»).")


@router.message(ApplyFlow.city_tz)
async def step_city_tz(m: Message, state: FSMContext):
    city_tz = (m.text or "").strip()
    if len(city_tz) < 2:
        await m.answer("Чуть подробнее, пожалуйста: город и часовой пояс.")
        return
    await state.update_data(city_tz=city_tz)
    await state.set_state(ApplyFlow.contact)
    un = f"@{m.from_user.username}" if m.from_user.username else "—"
    await m.answer(
        "Контакт для связи (телеграм/почта/телефон).\n"
        f"Можно написать ваш текущий ник: {un}"
    )


@router.message(ApplyFlow.contact)
async def step_contact(m: Message, state: FSMContext):
    contact = (m.text or "").strip()
    if len(contact) < 2:
        await m.answer("Нужен контакт — ник, телефон или email.")
        return
    await state.update_data(contact=contact)
    await state.set_state(ApplyFlow.motivation)
    await m.answer("Коротко ваша мотивация: почему хотите в трек? (1–2 предложения)")


@router.message(ApplyFlow.motivation)
async def step_motivation(m: Message, state: FSMContext):
    motivation = (m.text or "").strip()
    if len(motivation) < 5:
        await m.answer("Добавьте, пожалуйста, пару слов о мотивации.")
        return

    data = await state.get_data()
    name = data.get("name", "")
    city_tz = data.get("city_tz", "")
    contact = data.get("contact", "")

    # Сохраняем лид
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        if not u:
            await m.answer("Сначала пройдите /start.", reply_markup=main_menu())
            await state.clear()
            return

        note = f"name: {name}; city_tz: {city_tz}; motivation: {motivation}"
        lead = Lead(
            user_id=u.id,
            channel="tg",
            contact=contact,
            note=note,
            track="leader",
        )
        s.add(lead)

    await state.clear()
    await m.answer("Заявка принята ✅\nМы вернёмся с деталями.", reply_markup=main_menu())

    # Уведомление админам
    text = (
        "🆕 Новая заявка: «Путь лидера»\n"
        f"user_id={m.from_user.id} @{m.from_user.username or '-'}\n"
        f"Имя: {name}\nГород/часовой пояс: {city_tz}\nКонтакт: {contact}\n"
        f"Мотивация: {motivation}"
    )
    for aid in _admin_ids_set():
        try:
            await m.bot.send_message(aid, text)
        except Exception:
            pass
