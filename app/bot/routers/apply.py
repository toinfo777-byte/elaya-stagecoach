# app/bot/routers/apply.py
from __future__ import annotations

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

try:
    from app.keyboards.menu import get_main_menu_kb  # type: ignore
except Exception:
    get_main_menu_kb = None

router = Router(name="apply")

BACK_TO_MENU_TEXT = "📎 В меню"


class LeaderForm(StatesGroup):
    WAIT_GOAL = State()


def _only_menu_kb() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=BACK_TO_MENU_TEXT)]],
        resize_keyboard=True,
    )


def _main_menu_kb() -> types.ReplyKeyboardMarkup | None:
    if callable(get_main_menu_kb):
        try:
            return get_main_menu_kb()  # type: ignore[misc]
        except Exception:
            pass
    return None


async def _back_to_main_menu(message: types.Message, state: FSMContext | None = None) -> None:
    if state:
        await state.clear()
    kb = _main_menu_kb() or _only_menu_kb()
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=kb)


@router.message(Command("apply"))
@router.message(F.text.casefold() == "🧭 путь лидера")
@router.message(F.text.casefold() == "путь лидера")
async def apply_entry(message: types.Message, state: FSMContext) -> None:
    await state.set_state(LeaderForm.WAIT_GOAL)
    await message.answer(
        "Путь лидера: короткая заявка.\n"
        "Напишите, чего хотите достичь — одним сообщением (до 200 символов).\n"
        "Если передумали — /cancel.",
        reply_markup=_only_menu_kb(),
    )


@router.message(LeaderForm.WAIT_GOAL, F.text & ~F.text.startswith("/"))
async def apply_save(message: types.Message, state: FSMContext) -> None:
    goal = (message.text or "").strip()
    # TODO: здесь можно сохранить goal в БД/гугл-таблицу/что угодно
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍")
    await _back_to_main_menu(message, state)


@router.message(LeaderForm.WAIT_GOAL, Command("cancel"))
async def apply_cancel(message: types.Message, state: FSMContext) -> None:
    await message.answer("Отменил. Ничего не сохранил.")
    await _back_to_main_menu(message, state)


@router.message(F.text == BACK_TO_MENU_TEXT)
async def apply_back_to_menu(message: types.Message, state: FSMContext) -> None:
    await _back_to_main_menu(message, state)
