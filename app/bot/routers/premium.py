from __future__ import annotations

from aiogram import Router, F, types
from aiogram.filters import Text
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.menu import (
    BTN_PREMIUM,
    main_menu,
)
from app.storage.repo import session_scope, log_event
from app.storage.models import Lead, User

router = Router(name="premium")

# --- callbacks
CB_INSIDE = "premium:inside"
CB_APPLY = "premium:apply"
CB_LIST = "premium:list"
CB_BACK = "premium:back"


class PremiumForm(StatesGroup):
    waiting_goal = State()


def premium_kb() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔍 Что внутри", callback_data=CB_INSIDE)
    kb.button(text="📝 Оставить заявку", callback_data=CB_APPLY)
    kb.button(text="📋 Мои заявки", callback_data=CB_LIST)
    kb.button(text="📣 В меню", callback_data=CB_BACK)
    kb.adjust(1)
    return kb.as_markup()


@router.message(Text(BTN_PREMIUM))
async def premium_entry(message: types.Message) -> None:
    text = (
        "⭐️ <b>Расширенная версия</b>\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и «путь лидера»\n\n"
        "Выберите действие:"
    )
    await message.answer(text, reply_markup=premium_kb())


@router.callback_query(F.data == CB_INSIDE)
async def premium_inside(call: types.CallbackQuery) -> None:
    await call.answer()
    await call.message.answer(
        "Внутри расширенной версии — больше практики и персональных разборов."
    )


@router.callback_query(F.data == CB_APPLY)
async def premium_apply_start(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(PremiumForm.waiting_goal)
    await call.message.answer(
        "Напишите цель одной короткой фразой (до 200 символов). Если передумали — отправьте /cancel."
    )


@router.message(PremiumForm.waiting_goal)
async def premium_apply_save(message: types.Message, state: FSMContext) -> None:
    goal_text = (message.text or "").strip()[:200]

    with session_scope() as s:
        # гарантируем наличие пользователя
        tg_id = message.from_user.id
        user = s.query(User).filter_by(tg_id=tg_id).first()
        if user is None:
            user = User(
                tg_id=tg_id,
                username=message.from_user.username or None,
                name=message.from_user.full_name or None,
            )
            s.add(user)
            s.flush()

        # сохраняем лид
        contact = f"@{message.from_user.username}" if message.from_user.username else str(tg_id)
        lead = Lead(
            user_id=user.id,
            channel="tg",
            contact=contact,
            note=goal_text,
            track="premium",
        )
        s.add(lead)
        s.flush()

        # лог
        log_event(s, user_id=user.id, name="lead_created", payload={"track": "premium"})

    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍")
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())


@router.callback_query(F.data == CB_LIST)
async def premium_my_leads(call: types.CallbackQuery) -> None:
    await call.answer()
    tg_id = call.from_user.id

    with session_scope() as s:
        user = s.query(User).filter_by(tg_id=tg_id).first()
        if not user:
            await call.message.answer("Заявок пока нет.")
            return

        leads = (
            s.query(Lead)
            .filter(Lead.user_id == user.id)
            .order_by(Lead.ts.desc())
            .limit(10)
            .all()
        )

    if not leads:
        await call.message.answer("Заявок пока нет.")
        return

    lines = ["Мои заявки:"]
    for i, l in enumerate(leads, 1):
        lines.append(f"• #{i} — {l.ts:%d.%m %H:%M} — {l.track or 'без трека'}")

    await call.message.answer("\n".join(lines))


@router.callback_query(F.data == CB_BACK)
async def premium_back(call: types.CallbackQuery) -> None:
    await call.answer()
    await call.message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
