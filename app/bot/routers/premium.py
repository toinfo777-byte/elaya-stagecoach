from __future__ import annotations

from datetime import datetime
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.keyboards.menu import (
    main_menu,
    BTN_PREMIUM,      # ⭐️ Расширенная версия (нижнее меню)
)
from app.storage.repo import session_scope, log_event
from app.storage.models import Lead, User

router = Router(name="premium")


# --------- локальная клавиатура «Расширенная версия» ----------
BTN_PREM_WHATS_INSIDE = "🔍 Что внутри"
BTN_PREM_APPLY       = "📝 Оставить заявку"
BTN_PREM_MY_APPLIES  = "📄 Мои заявки"
BTN_PREM_BACK        = "📣 В меню"

def premium_menu_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=BTN_PREM_WHATS_INSIDE)],
        [KeyboardButton(text=BTN_PREM_APPLY)],
        [KeyboardButton(text=BTN_PREM_MY_APPLIES)],
        [KeyboardButton(text=BTN_PREM_BACK)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


# --------- FSM ---------
class PremiumForm(StatesGroup):
    goal = State()


# --------- entry точки ---------
@router.message(F.text == BTN_PREMIUM)
@router.message(F.text == "⭐️ Расширенная версия")  # на всякий случай
async def premium_entry(msg: Message) -> None:
    text = (
        "⭐️ <b>Расширенная версия</b>\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и «путь лидера»\n\n"
        "Выберите действие:"
    )
    await msg.answer(text, reply_markup=premium_menu_kb())
    await log_event_safe(msg.from_user.id, "premium_open")


@router.message(F.text == BTN_PREM_WHATS_INSIDE)
async def premium_inside(msg: Message) -> None:
    await msg.answer(
        "Внутри расширенной версии — больше практики и персональных разборов.",
        reply_markup=premium_menu_kb(),
    )


@router.message(F.text == BTN_PREM_MY_APPLIES)
async def premium_my_applies(msg: Message) -> None:
    tg_id = msg.from_user.id
    with session_scope() as s:
        user = s.query(User).filter_by(tg_id=tg_id).first()
        if not user:
            await msg.answer("Заявок пока нет.", reply_markup=premium_menu_kb())
            return
        leads = (
            s.query(Lead)
            .filter_by(user_id=user.id, track="premium")
            .order_by(Lead.ts.desc())
            .limit(10)
            .all()
        )
    if not leads:
        await msg.answer("Заявок пока нет.", reply_markup=premium_menu_kb())
        return

    lines = []
    for i, l in enumerate(leads, 1):
        when = l.ts.strftime("%d.%m %H:%M")
        status = "🟡 новая"  # пока без статусов
        lines.append(f"• #{i} — {when} — {status}")

    await msg.answer("Мои заявки:\n" + "\n".join(lines), reply_markup=premium_menu_kb())


@router.message(F.text == BTN_PREM_APPLY)
async def premium_apply_start(msg: Message, state: FSMContext) -> None:
    await state.set_state(PremiumForm.goal)
    await msg.answer(
        "Напишите цель одной короткой фразой (до 200 символов). Если передумали — отправьте /cancel.",
        reply_markup=premium_menu_kb(),  # оставим то же меню, это ок
    )


@router.message(PremiumForm.goal)
async def premium_apply_save(msg: Message, state: FSMContext) -> None:
    text = (msg.text or "").strip()
    if not text:
        await msg.answer("Нужно написать цель одной фразой. Или /cancel.")
        return

    tg_id = msg.from_user.id
    username = (msg.from_user.username or "").strip()
    contact = f"@{username}" if username else str(tg_id)

    with session_scope() as s:
        # гарантируем пользователя
        user = s.query(User).filter_by(tg_id=tg_id).first()
        if not user:
            user = User(tg_id=tg_id, username=username, last_seen=datetime.utcnow())
            s.add(user)
            s.flush()

        s.add(
            Lead(
                user_id=user.id,
                channel="tg",
                contact=contact,
                note=text[:500],
                track="premium",
            )
        )

    await state.clear()
    # ВАЖНО: после успешной заявки возвращаем ГЛАВНОЕ меню,
    # чтобы не висела кнопка «Оставить заявку»
    await msg.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=main_menu())
    await log_event_safe(tg_id, "lead_premium_created", {"text": text})


@router.message(F.text == BTN_PREM_BACK)
async def premium_back_to_menu(msg: Message, state: FSMContext) -> None:
    await state.clear()
    await msg.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())


# --------- вспомогательное ---------
async def log_event_safe(tg_id: int, name: str, payload: dict | None = None) -> None:
    try:
        with session_scope() as s:
            user = s.query(User).filter_by(tg_id=tg_id).first()
            log_event(s, user_id=(user.id if user else None), name=name, payload=(payload or {}))
    except Exception:
        pass
