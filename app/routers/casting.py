from __future__ import annotations

import re
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.keyboards.reply import main_menu_kb
from app.keyboards.inline import casting_skip_kb  # callback_data: "cast:skip_url"
from app.utils.admin import notify_admin
from app.storage.repo_extras import save_casting  # безопасная заглушка

router = Router(name="casting")

# ---- Фоллбэк: если нет flows/casting_flow.py, объявим стейты и старт тут ----
try:
    from app.flows.casting_flow import start_casting_flow, ApplyForm  # type: ignore
except Exception:
    from aiogram.fsm.state import StatesGroup, State

    class ApplyForm(StatesGroup):
        name = State()
        age = State()
        city = State()
        experience = State()
        contact = State()
        portfolio = State()

    async def start_casting_flow(m: Message, state: FSMContext):
        await state.clear()
        await state.set_state(ApplyForm.name)
        await m.answer("Как тебя зовут?")

HTTP_RE = re.compile(r"^https?://", re.I)

# ВНИМАНИЕ: Больше НЕ перехватываем /casting и кнопку 🎭 — это мини-кастинг.
# Если хочешь запускать длинную форму вручную — оставил скрытую команду:
@router.message(StateFilter("*"), Command("apply_form"))
async def casting_entry(m: Message, state: FSMContext):
    await start_casting_flow(m, state)


# ==== ВОПРОСЫ ====
@router.message(StateFilter(ApplyForm.name))
async def q_name(m: Message, state: FSMContext):
    await state.update_data(name=(m.text or "").strip())
    await state.set_state(ApplyForm.age)
    await m.answer("Сколько тебе лет?")


@router.message(StateFilter(ApplyForm.age))
async def q_age(m: Message, state: FSMContext):
    try:
        age = int((m.text or "").strip())
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
    await state.update_data(city=(m.text or "").strip())
    await state.set_state(ApplyForm.experience)
    await m.answer("Какой у тебя опыт?\n– нет\n– 1–2 года\n– 3+ лет")


@router.message(StateFilter(ApplyForm.experience))
async def q_exp(m: Message, state: FSMContext):
    await state.update_data(experience=(m.text or "").strip())
    await state.set_state(ApplyForm.contact)
    await m.answer("Контакт для связи\n@username / телефон / email")


@router.message(StateFilter(ApplyForm.contact))
async def q_contact(m: Message, state: FSMContext):
    await state.update_data(contact=(m.text or "").strip())
    await state.set_state(ApplyForm.portfolio)
    await m.answer("Ссылка на портфолио (если есть)", reply_markup=casting_skip_kb())


# ==== ПОРТФОЛИО (опционально) ====
@router.callback_query(StateFilter(ApplyForm.portfolio), F.data == "cast:skip_url")
async def skip_portfolio(cb: CallbackQuery, state: FSMContext):
    await state.update_data(portfolio=None)
    await _finish(cb.message, state)
    await cb.answer()


@router.message(StateFilter(ApplyForm.portfolio), F.text.casefold().in_({"пропустить", "нет", "пусто"}))
async def portfolio_skip_text(m: Message, state: FSMContext):
    await state.update_data(portfolio=None)
    await _finish(m, state)


@router.message(StateFilter(ApplyForm.portfolio), F.text)
async def q_portfolio(m: Message, state: FSMContext):
    text = (m.text or "").strip()
    if text.startswith("/"):
        return  # дай пройти глобальным командам
    if HTTP_RE.match(text):
        await state.update_data(portfolio=text)
        await _finish(m, state)
    else:
        await m.answer("Нужна ссылка (http/https) или нажми «Пропустить».")


# ==== ФИНИШ ====
async def _finish(m: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    # вызываем безопасную заглушку
    save_casting(
        tg_id=m.from_user.id,
        name=str(data.get("name", "")),
        age=int(data.get("age", 0) or 0),
        city=str(data.get("city", "")),
        experience=str(data.get("experience", "")),
        contact=str(data.get("contact", "")),
        portfolio=data.get("portfolio"),
        agree_contact=True,
    )

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

    await m.answer("✅ Заявка принята! Мы свяжемся в течение 1–2 дней.", reply_markup=main_menu_kb())
