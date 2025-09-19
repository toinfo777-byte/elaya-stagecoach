from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.keyboards.menu import BTN_APPLY, main_menu
from app.storage.repo import session_scope, log_event
from app.storage.models import User, Lead
from app.config import settings

router = Router(name="apply")


def kb_apply() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="Оставить заявку")],
        [KeyboardButton(text="📣 В меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


class ApplySG(StatesGroup):
    waiting_goal = State()


@router.message(Command("apply"))
@router.message(F.text == BTN_APPLY)
async def apply_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Путь лидера — индивидуальная траектория с фокусом на цели.\n"
        "Оставьте заявку — вернусь с вопросами и предложениями.",
        reply_markup=kb_apply(),
    )


@router.message(F.text.lower().in_({"📣 в меню", "в меню"}))
async def apply_back_to_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())


@router.message(F.text.lower().in_({"оставить заявку"}))
async def apply_ask_goal(message: Message, state: FSMContext) -> None:
    await state.set_state(ApplySG.waiting_goal)
    await message.answer(
        "Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — /cancel.",
    )


@router.message(ApplySG.waiting_goal, F.text.len() > 0)
async def apply_save_goal(message: Message, state: FSMContext) -> None:
    goal = (message.text or "").strip()
    if not goal:
        await message.answer("Пусто. Напишите кратко цель.")
        return
    if len(goal) > 200:
        await message.answer("Слишком длинно 🙈 Сократите до 200 символов, пожалуйста.")
        return

    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=message.from_user.id).first()
        if not u:
            u = User(tg_id=message.from_user.id, username=message.from_user.username or None, name=message.from_user.full_name)
            s.add(u)
            s.commit()

        s.add(Lead(
            user_id=u.id,
            channel="tg",
            contact=f"@{u.username}" if u.username else str(u.tg_id),
            note=goal,
            track="apply",
        ))
        s.commit()
        log_event(s, u.id, "apply_request", {"goal": goal})

    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=main_menu())
