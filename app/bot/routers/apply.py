from __future__ import annotations

from datetime import datetime
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.menu import main_menu, BTN_APPLY
from app.storage.repo import session_scope, log_event
from app.storage.models import Lead, User

router = Router(name="apply")


class ApplyForm(StatesGroup):
    goal = State()


@router.message(F.text == BTN_APPLY)
@router.message(F.text == "🧭 Путь лидера")
@router.message(F.text == "/apply")
async def apply_entry(msg: Message, state: FSMContext) -> None:
    await state.set_state(ApplyForm.goal)
    await msg.answer(
        "Путь лидера — индивидуальная траектория с фокусом на цели.\n"
        "Оставьте заявку — вернусь с вопросами и предложениями.\n\n"
        "Напишите цель одной короткой фразой (до 200 символов). Если передумали — отправьте /cancel."
    )
    await log_event_safe(msg.from_user.id, "apply_open")


@router.message(ApplyForm.goal)
async def apply_save(msg: Message, state: FSMContext) -> None:
    text = (msg.text or "").strip()
    if not text:
        await msg.answer("Нужно написать цель одной фразой. Или /cancel.")
        return

    tg_id = msg.from_user.id
    username = (msg.from_user.username or "").strip()
    contact = f"@{username}" if username else str(tg_id)

    with session_scope() as s:
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
                track="apply",
            )
        )

    await state.clear()
    # Сразу возвращаем основное меню, чтобы избежать «залипания» любого подменю
    await msg.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=main_menu())
    await log_event_safe(tg_id, "lead_apply_created", {"text": text})


# универсальный /cancel
@router.message(F.text == "/cancel")
async def apply_cancel(msg: Message, state: FSMContext) -> None:
    await state.clear()
    await msg.answer("Отменил. Возвращаемся в меню.", reply_markup=main_menu())


async def log_event_safe(tg_id: int, name: str, payload: dict | None = None) -> None:
    try:
        with session_scope() as s:
            user = s.query(User).filter_by(tg_id=tg_id).first()
            log_event(s, user_id=(user.id if user else None), name=name, payload=(payload or {}))
    except Exception:
        pass
