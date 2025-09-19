# app/bot/routers/premium.py
from __future__ import annotations

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.keyboards.menu import (
    BTN_PREMIUM,  # "⭐️ Расширенная версия"
    main_menu,
)
from app.storage.repo import session_scope
from app.storage.models import User, Lead

router = Router(name="premium")


# ——— Локальные кнопки раздела «Расширенная версия»
PRE_BTN_WHATS_INSIDE = "📦 Что внутри"
PRE_BTN_LEAVE = "📝 Оставить заявку"
PRE_BTN_MY_LEADS = "🗂 Мои заявки"
PRE_BTN_BACK = "📣 В меню"


def premium_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=PRE_BTN_WHATS_INSIDE)],
        [KeyboardButton(text=PRE_BTN_LEAVE)],
        [KeyboardButton(text=PRE_BTN_MY_LEADS)],
        [KeyboardButton(text=PRE_BTN_BACK)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


class PremiumStates(StatesGroup):
    wait_goal = State()


def _ensure_user(session, msg: types.Message) -> User:
    tg_id = msg.from_user.id
    user = session.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        user = User(
            tg_id=msg.from_user.id,
            username=msg.from_user.username or None,
            name=(msg.from_user.first_name or "")
            + ((" " + msg.from_user.last_name) if msg.from_user.last_name else ""),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


# ——— вход в раздел
@router.message(F.text == BTN_PREMIUM)
@router.message(F.text == "/premium")
async def premium_entry(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "⭐️ <b>Расширенная версия</b>\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и «путь лидера»\n\n"
        "Выберите действие:",
        reply_markup=premium_kb(),
    )


# ——— Подкнопки
@router.message(F.text == PRE_BTN_WHATS_INSIDE)
async def premium_whats_inside(msg: types.Message):
    await msg.answer(
        "Внутри расширенной версии — больше практики и персональных разборов.",
        reply_markup=premium_kb(),
    )


@router.message(F.text == PRE_BTN_MY_LEADS)
async def premium_my_leads(msg: types.Message):
    with session_scope() as s:
        user = s.query(User).filter(User.tg_id == msg.from_user.id).first()
        if not user:
            await msg.answer("Заявок пока нет.", reply_markup=premium_kb())
            return

        leads = (
            s.query(Lead)
            .filter(Lead.user_id == user.id)
            .order_by(Lead.ts.desc())
            .limit(10)
            .all()
        )

    if not leads:
        await msg.answer("Заявок пока нет.", reply_markup=premium_kb())
        return

    lines = []
    for i, lead in enumerate(leads, 1):
        lines.append(f"#{i} — {lead.ts:%d.%m %H:%M} — {lead.track or '—'}")
    await msg.answer("Мои заявки:\n" + "\n".join(lines), reply_markup=premium_kb())


@router.message(F.text == PRE_BTN_BACK)
async def premium_back(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())


# ——— «Оставить заявку» (FSM)
@router.message(F.text == PRE_BTN_LEAVE)
async def premium_leave_start(msg: types.Message, state: FSMContext):
    await state.set_state(PremiumStates.wait_goal)
    await msg.answer(
        "Напишите цель одной короткой фразой (до 200 символов). Если передумали — отправьте /cancel."
    )


@router.message(PremiumStates.wait_goal, F.text)
async def premium_leave_save(msg: types.Message, state: FSMContext):
    txt = (msg.text or "").strip()
    if not txt:
        await msg.answer("Пришлите, пожалуйста, цель одной короткой фразой.")
        return

    with session_scope() as s:
        user = _ensure_user(s, msg)
        s.add(
            Lead(
                user_id=user.id,
                channel="tg",
                contact=msg.from_user.username or str(msg.from_user.id),
                note=txt[:500],
                track="premium",
            )
        )
        s.commit()

    await state.clear()
    # ВАЖНО: сразу уводим на главное меню, чтобы не оставалась «Оставить заявку» внизу
    await msg.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=main_menu())
