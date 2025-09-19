# app/bot/routers/apply.py
from __future__ import annotations

from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import (
    main_menu,
    BTN_APPLY,         # 🧭 Путь лидера
)
from app.storage.models import User, Lead
from app.storage.repo import session_scope

router = Router(name="apply")


# ----- FSM -----
class ApplyForm(StatesGroup):
    waiting_text = State()   # ждём «цель одной фразой»


# ----- Вспомогательное -----
def _contact_from_tg(user: types.User) -> str:
    if user.username:
        return f"@{user.username}"
    return f"tg:{user.id}"


def _get_or_create_user(tg_user: types.User) -> User:
    with session_scope() as s:
        u: User | None = s.query(User).filter_by(tg_id=tg_user.id).first()
        if u is None:
            u = User(
                tg_id=tg_user.id,
                username=tg_user.username,
                name=tg_user.full_name,
            )
            s.add(u)
            s.commit()
            s.refresh(u)
        return u


# ----- Клавиатуры локальные -----
def apply_kb() -> types.ReplyKeyboardMarkup:
    rows = [
        [types.KeyboardButton(text="Оставить заявку")],
        [types.KeyboardButton(text="📯 В меню")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


# ----- Хендлеры -----
@router.message(Command("apply"))
@router.message(F.text == BTN_APPLY)
async def open_apply(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Путь лидера — индивидуальная траектория с фокусом на цели.\n"
        "Оставьте заявку — вернусь с вопросами и предложениями.",
        reply_markup=apply_kb(),
    )


@router.message(F.text == "Оставить заявку")
async def apply_start(message: types.Message, state: FSMContext) -> None:
    await state.set_state(ApplyForm.waiting_text)
    await message.answer(
        "Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — отправьте /cancel.",
    )


@router.message(Command("cancel"), StateFilter(ApplyForm.waiting_text))
async def apply_cancel(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())


@router.message(StateFilter(ApplyForm.waiting_text))
async def apply_save_text(message: types.Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Пришлите, пожалуйста, цель одной фразой.")
        return

    # Сохраняем заявку в leads (track='leader')
    u = _get_or_create_user(message.from_user)
    with session_scope() as s:
        s.add(Lead(
            user_id=u.id,
            channel="tg",
            contact=_contact_from_tg(message.from_user),
            note=text[:500],
            track="leader",
        ))
        s.commit()

    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=main_menu())
