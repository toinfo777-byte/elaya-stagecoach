# app/bot/routers/premium.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.keyboards.menu import BTN_PREMIUM, main_menu

router = Router(name="premium")

# Локальные кнопки внутри раздела
KB_WHATS_INSIDE = "🔎 Что внутри"
KB_LEAVE_APP = "📝 Оставить заявку"
KB_BACK_MENU = "📣 В меню"


def _premium_kb() -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=KB_WHATS_INSIDE)],
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


class PremiumForm(StatesGroup):
    goal = State()  # короткая цель/заявка


@router.message(F.text == BTN_PREMIUM)
async def premium_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "⭐️ <b>Расширенная версия</b>\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и «путь лидера»\n\n"
        "Выберите действие:",
        reply_markup=_premium_kb(),
    )


@router.message(F.text == KB_WHATS_INSIDE)
async def premium_inside(message: Message) -> None:
    await message.answer(
        "Внутри расширенной версии — больше практики и персональных разборов.",
        reply_markup=_premium_kb(),
    )


@router.message(F.text == KB_LEAVE_APP)
async def premium_ask_application(message: Message, state: FSMContext) -> None:
    await state.set_state(PremiumForm.goal)
    await message.answer(
        "Напишите цель одной короткой фразой (до 200 символов). "
        "Если передумали — отправьте /cancel.",
        reply_markup=_only_menu_kb(),
    )


@router.message(PremiumForm.goal)
async def premium_take_application(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Пусто. Напишите коротко вашу цель, пожалуйста.")
        return

    # тут можно сохранить в БД/логах, если нужно
    try:
        from app.storage.repo import session_scope, log_event  # type: ignore
        from app.storage.models import User  # type: ignore

        with session_scope() as s:
            u = s.query(User).filter_by(tg_id=message.from_user.id).first()
            uid = u.id if u else None
            log_event(s, uid, "premium_application", {"text": text})
    except Exception:
        # логирование необязательно — не мешаем потоку
        pass

    await state.clear()
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=_only_menu_kb())


@router.message(F.text == KB_BACK_MENU)
async def back_to_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=main_menu())


# Общее /cancel — на всякий случай
@router.message(F.text.casefold() == "/cancel")
async def cancel_any(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Отменил. Вернул в меню.", reply_markup=main_menu())
