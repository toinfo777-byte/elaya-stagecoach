# app/bot/routers/apply.py
from __future__ import annotations

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.keyboards.menu import BTN_APPLY, main_menu
from app.storage.repo import session_scope
from app.storage.models import User, Lead

router = Router(name="apply")


class ApplyStates(StatesGroup):
    wait_goal = State()


def _user_from_message(m: types.Message) -> dict:
    u = m.from_user
    return {
        "tg_id": u.id,
        "username": u.username or None,
        "name": (u.first_name or "") + ((" " + u.last_name) if u.last_name else ""),
    }


def _ensure_user(session, msg: types.Message) -> User:
    tg_id = msg.from_user.id
    user = session.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        payload = _user_from_message(msg)
        user = User(**payload)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


@router.message(F.text == BTN_APPLY)
@router.message(F.text == "/apply")
async def apply_entry(msg: types.Message, state: FSMContext):
    """
    Нажали «🧭 Путь лидера» — сразу просим короткую цель одной фразой.
    """
    await state.set_state(ApplyStates.wait_goal)
    await msg.answer(
        "Путь лидера — индивидуальная траектория с фокусом на цели.\n"
        "Напишите цель одной короткой фразой (до 200 символов). "
        "Если передумали — отправьте /cancel.",
    )


@router.message(ApplyStates.wait_goal, F.text)
async def apply_save_goal(msg: types.Message, state: FSMContext):
    text = (msg.text or "").strip()
    if not text:
        await msg.answer("Пришлите, пожалуйста, цель одной короткой фразой.")
        return

    # Сохраняем лид
    with session_scope() as s:
        user = _ensure_user(s, msg)
        s.add(
            Lead(
                user_id=user.id,
                channel="tg",
                contact=msg.from_user.username or str(msg.from_user.id),
                note=text[:500],
                track="leader",
            )
        )
        s.commit()

    # Завершаем сценарий и возвращаем в главное меню
    await state.clear()
    await msg.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=main_menu())
