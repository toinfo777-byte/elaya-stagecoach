# app/routers/casting.py
from __future__ import annotations

import re
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.keyboards.menu import main_menu, BTN_CASTING, BTN_APPLY
from app.keyboards.inline import casting_skip_kb
from app.utils.admin import notify_admin
from app.storage.repo import save_casting

router = Router(name="casting")


class ApplyForm(StatesGroup):
    name = State()
    age = State()
    city = State()
    experience = State()
    contact = State()
    portfolio = State()


def _looks_like_url(text: str) -> bool:
    return bool(re.match(r"^https?://", text.strip(), re.I))


# ==== СТАРТ ====
@router.message(Command("casting"), StateFilter(None))
@router.message(F.text.in_({BTN_CASTING, BTN_APPLY}), StateFilter(None))
async def start_casting(m: Message, state: FSMContext):
    await state.set_state(ApplyForm.name)
    await m.answer("Как тебя зовут?\n<i>Имя и фамилия</i>")


# ==== ВОПРОСЫ ====
@router.message(StateFilter(ApplyForm.name))
async def q_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text.strip())
    await state.set_state(ApplyForm.age)
    await m.answer("Сколько тебе лет?")


@router.message(StateFilter(ApplyForm.age))
async def q_age(m: Message, state: FSMContext):
    try:
        age = int(m.text.strip())
        if not (10 <= age <= 99):
            raise ValueError
    except Exception:
        await m.answer("Допустимый диапазон: 10–99. Введи число.")
        return
    await state.update_data(age=age)
    await state.set_state(ApplyForm.city)
    await m.answer("Из какого ты города?")


@router.message(StateFilter(ApplyForm.city))
async def q_city(m: Message, state: FSMContext):
    await state.update_data(city=m.text.strip())
    await state.set_state(ApplyForm.experience)
    await m.answer("Какой у тебя опыт?\n– нет\n– 1–2 года\n– 3+ лет")


@router.message(StateFilter(ApplyForm.experience))
async def q_exp(m: Message, state: FSMContext):
    await state.update_data(experience=m.text.strip())
    await state.set_state(ApplyForm.contact)
    await m.answer("Контакт для связи\n@username / телефон / email")


@router.message(StateFilter(ApplyForm.contact))
async def q_contact(m: Message, state: FSMContext):
    await state.update_data(contact=m.text.strip())
    await state.set_state(ApplyForm.portfolio)
    await m.answer("Ссылка на портфолио (если есть)", reply_markup=casting_skip_kb())


# ==== ПОРТФОЛИО (опционально) ====
@router.callback_query(F.data == "casting:skip_portfolio", StateFilter(ApplyForm.portfolio))
async def skip_portfolio(c: CallbackQuery, state: FSMContext):
    await state.update_data(portfolio=None)
    await _finish(c.message, state)
    await c.answer()


@router.message(StateFilter(ApplyForm.portfolio))
async def q_portfolio(m: Message, state: FSMContext):
    text = (m.text or "").strip()
    portfolio = text if _looks_like_url(text) else None
    await state.update_data(portfolio=portfolio)
    await _finish(m, state)


# ==== ФИНИШ ====
async def _finish(m: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    # Сохраняем в БД
    await save_casting(
        tg_id=m.from_user.id,
        name=str(data.get("name", "")),
        age=int(data.get("age", 0) or 0),
        city=str(data.get("city", "")),
        experience=str(data.get("experience", "")),
        contact=str(data.get("contact", "")),
        portfolio=data.get("portfolio"),
        agree_contact=True,
    )

    # Уведомление админу
    summary = (
        "🎭 Новая заявка (кастинг / путь лидера)\n"
        f"Имя: {data.get('name')}\n"
        f"Возраст: {data.get('age')}\n"
        f"Город: {data.get('city')}\n"
        f"Опыт: {data.get('experience')}\n"
        f"Контакт: {data.get('contact')}\n"
        f"Портфолио: {data.get('portfolio') or '—'}\n"
        f"От: @{m.from_user.username or m.from_user.id}"
    )
    await notify_admin(summary, m.bot)

    await m.answer("✅ Заявка принята! Мы свяжемся в течение 1–2 дней.", reply_markup=main_menu())


# ==== ФОРСИРОВАННЫЙ ВЫХОД ====
@router.message(Command("menu"))
async def force_menu(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Меню", reply_markup=main_menu())
