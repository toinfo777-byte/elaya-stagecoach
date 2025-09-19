from __future__ import annotations

from aiogram import Router, F, types
from aiogram.filters import Text
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.menu import BTN_APPLY, main_menu
from app.storage.repo import session_scope, log_event
from app.storage.models import Lead, User

router = Router(name="apply")

# --- callbacks
CB_APPLY_START = "apply:start"
CB_APPLY_LIST = "apply:list"
CB_APPLY_BACK = "apply:back"


class ApplyForm(StatesGroup):
    waiting_goal = State()


def apply_kb() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Оставить заявку", callback_data=CB_APPLY_START)
    kb.button(text="📋 Мои заявки", callback_data=CB_APPLY_LIST)
    kb.button(text="📣 В меню", callback_data=CB_APPLY_BACK)
    kb.adjust(1)
    return kb.as_markup()


@router.message(Text(BTN_APPLY))
async def apply_entry(message: types.Message) -> None:
    text = (
        "Путь лидера — индивидуальная траектория с фокусом на цели.\n"
        "Оставьте заявку — вернусь с вопросами и предложениями."
    )
    await message.answer(text, reply_markup=apply_kb())


@router.callback_query(F.data == CB_APPLY_START)
async def apply_goal_ask(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(ApplyForm.waiting_goal)
    await call.message.answer(
        "Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — отправьте /cancel."
    )


@router.message(ApplyForm.waiting_goal)
async def apply_goal_save(message: types.Message, state: FSMContext) -> None:
    goal = (message.text or "").strip()[:200]

    with session_scope() as s:
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

        contact = f"@{message.from_user.username}" if message.from_user.username else str(tg_id)
        lead = Lead(
            user_id=user.id,
            channel="tg",
            contact=contact,
            note=goal,
            track="leader",  # отличаем от premium
        )
        s.add(lead)
        s.flush()

        log_event(s, user_id=user.id, name="lead_created", payload={"track": "leader"})

    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍")
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())


@router.callback_query(F.data == CB_APPLY_LIST)
async def apply_list(call: types.CallbackQuery) -> None:
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


@router.callback_query(F.data == CB_APPLY_BACK)
async def apply_back(call: types.CallbackQuery) -> None:
    await call.answer()
    await call.message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
