# app/bot/routers/apply.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import BTN_APPLY, main_menu

router = Router(name="apply")

KB_LEAVE_APP = "📝 Оставить заявку"
KB_BACK_MENU = "📣 В меню"


def _apply_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=KB_LEAVE_APP)],
        [KeyboardButton(text=KB_BACK_MENU)],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


def _only_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=KB_BACK_MENU)]],
        resize_keyboard=True,
        is_persistent=True,
    )


class ApplyForm(StatesGroup):
    goal = State()


@router.message(F.text == BTN_APPLY)
async def apply_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Путь лидера — индивидуальная траектория с фокусом на цели.\n"
        "Оставьте заявку — вернусь с вопросами и предложениями.",
        reply_markup=_apply_kb(),
    )


@router.message(F.text == KB_LEAVE_APP)
async def apply_ask(message: Message, state: FSMContext) -> None:
    await state.set_state(ApplyForm.goal)
    await message.answer(
        "Короткая заявка. Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — отправьте /cancel.",
        reply_markup=_only_menu_kb(),
    )


@router.message(ApplyForm.goal)
async def apply_take(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Пусто. Напишите коротко вашу цель, пожалуйста.")
        return

    # сохраняем как событие/лид — необязательно, но полезно
    try:
        from app.storage.repo import session_scope, log_event  # type: ignore
        from app.storage.models import User  # type: ignore

        with session_scope() as s:
            u = s.query(User).filter_by(tg_id=message.from_user.id).first()
            uid = u.id if u else None
            log_event(s, uid, "apply_application", {"text": text})
    except Exception:
        pass

    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=_only_menu_kb())


@router.message(F.text == KB_BACK_MENU)
async def back_to_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())


@router.message(F.text.casefold() == "/cancel")
async def cancel_any(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Отменил. Вернул в меню.", reply_markup=main_menu())
