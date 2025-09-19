from __future__ import annotations

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy import text

from app.keyboards.menu import BTN_APPLY
from app.storage.repo import SessionLocal

router = Router(name="apply")


class ApplyForm(StatesGroup):
    waiting_goal = State()


def _ensure_user_and_get_id(telegram_id: int, username: str | None) -> int:
    from sqlalchemy import text
    from app.storage.repo import SessionLocal

    with SessionLocal() as s:
        row = s.execute(
            text("SELECT id FROM users WHERE tg_id = :tg"),
            {"tg": telegram_id},
        ).fetchone()
        if row:
            return int(row[0])

        s.execute(
            text("INSERT INTO users (tg_id, username, streak) VALUES (:tg, :un, 0)"),
            {"tg": telegram_id, "un": username or None},
        )
        s.commit()
        row = s.execute(
            text("SELECT id FROM users WHERE tg_id = :tg"),
            {"tg": telegram_id},
        ).fetchone()
        return int(row[0])


# вход в раздел
@router.message(Command("apply"))
@router.message(F.text == BTN_APPLY, state="*")
async def apply_entry(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Путь лидера — индивидуальная траектория с фокусом на цели.\n"
        "Оставьте заявку — вернусь с вопросами и предложениями.",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Оставить заявку", callback_data="apply:req"),
                types.InlineKeyboardButton(text="📣 В меню", callback_data="apply:menu"),
            ]
        ]),
    )


@router.callback_query(F.data == "apply:menu", state="*")
async def apply_back(cb: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.")
    await cb.answer()


@router.callback_query(F.data == "apply:req", state="*")
async def apply_req_start(cb: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ApplyForm.waiting_goal)
    await cb.message.answer(
        "Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — /cancel."
    )
    await cb.answer()


@router.message(Command("cancel"), ApplyForm.waiting_goal)
async def apply_cancel(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Отменил. Готово — вернулся в меню.")


@router.message(ApplyForm.waiting_goal)
async def apply_save(message: types.Message, state: FSMContext) -> None:
    user_id = _ensure_user_and_get_id(
        message.from_user.id, getattr(message.from_user, "username", None)
    )
    goal_text = (message.text or "").strip()[:200]

    # Сохраним как «лид» (таблица leads), чтобы заявка не терялась
    with SessionLocal() as s:
        s.execute(
            text(
                "INSERT INTO leads (user_id, channel, contact, note, track) "
                "VALUES (:uid, 'tg', :contact, :note, 'leader')"
            ),
            {
                "uid": user_id,
                "contact": f"@{getattr(message.from_user, 'username', '')}".strip("@"),
                "note": goal_text,
            },
        )
        s.commit()

    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍")
