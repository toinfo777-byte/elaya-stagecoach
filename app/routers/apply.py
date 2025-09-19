# app/routers/apply.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from app.keyboards.menu import BTN_APPLY, main_menu
from app.storage.repo import session_scope
from app.storage.models import User, Lead

router = Router(name="apply")

# --- локальные кнопки ---
BTN_BACK_TO_MENU = "📣 В меню"
BTN_LEAVE_REQUEST = "📝 Оставить заявку"

def apply_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=BTN_LEAVE_REQUEST)],
        [KeyboardButton(text=BTN_BACK_TO_MENU)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


class ApplyFSM(StatesGroup):
    waiting_short_goal = State()


# --- вход в раздел / кнопка ---
@router.message(Command("apply"))
@router.message(F.text == BTN_APPLY)
async def apply_entry(msg: Message) -> None:
    text = (
        "Путь лидера — индивидуальная траектория с фокусом на цели.\n"
        "Оставьте заявку — вернусь с вопросами и предложениями."
    )
    await msg.answer(text, reply_markup=apply_kb())


# --- «оставить заявку» — запускаем FSM ---
@router.message(F.text == BTN_LEAVE_REQUEST)
async def apply_start_collect(msg: Message, state: FSMContext) -> None:
    await state.set_state(ApplyFSM.waiting_short_goal)
    await msg.answer(
        "Напишите цель одной короткой фразой (до 200 символов). Если передумали — отправьте /cancel.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=BTN_BACK_TO_MENU)]],
            resize_keyboard=True,
            is_persistent=True,
        ),
    )


# --- получаем цель от пользователя ---
@router.message(ApplyFSM.waiting_short_goal, F.text.len() > 0)
async def apply_save_goal(msg: Message, state: FSMContext) -> None:
    goal = msg.text.strip()
    u = msg.from_user

    with session_scope() as s:
        user = s.query(User).filter_by(tg_id=u.id).first()
        if not user:
            user = User(
                tg_id=u.id,
                username=u.username or None,
                name=(u.full_name or u.first_name or None),
            )
            s.add(user)
            s.flush()

        contact = f"@{u.username}" if u.username else str(u.id)
        s.add(
            Lead(
                user_id=user.id,
                channel="tg",
                contact=contact,
                note=goal,
                track="leader",
            )
        )

    await state.clear()
    await msg.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=apply_kb())


# --- выход в главное меню ---
@router.message(F.text == BTN_BACK_TO_MENU)
async def apply_back_to_menu(msg: Message, state: FSMContext) -> None:
    await state.clear()
    await msg.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())
