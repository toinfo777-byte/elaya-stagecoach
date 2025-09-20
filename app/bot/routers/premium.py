# app/bot/routers/premium.py
from __future__ import annotations

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Необязательный импорт готовой клавиатуры меню, если у тебя она есть
try:
    from app.keyboards.menu import get_main_menu_kb  # type: ignore
except Exception:
    get_main_menu_kb = None

router = Router(name="premium")

BACK_TO_MENU_TEXT = "📎 В меню"


class PremiumForm(StatesGroup):
    WAIT_GOAL = State()


def _only_menu_kb() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=BACK_TO_MENU_TEXT)]],
        resize_keyboard=True,
    )


def _inline_actions_kb() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🔎 Что внутри", callback_data="premium:inside")],
            [types.InlineKeyboardButton(text="📝 Оставить заявку", callback_data="premium:apply")],
            [types.InlineKeyboardButton(text="📂 Мои заявки", callback_data="premium:list")],
        ]
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
    menu_kb = _main_menu_kb() or _only_menu_kb()
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=menu_kb)


@router.message(Command("premium"))
@router.message(F.text.casefold() == "⭐ расширенная версия")
@router.message(F.text.casefold() == "расширенная версия")
async def premium_entry(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    text = (
        "⭐ <b>Расширенная версия</b>\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и «путь лидера»\n\n"
        "Выберите действие:"
    )
    # Внизу — только «В меню»
    await message.answer(text, reply_markup=_only_menu_kb())
    # А действия — инлайном
    await message.answer(" ", reply_markup=_inline_actions_kb())


@router.callback_query(F.data == "premium:inside")
async def premium_inside(cb: types.CallbackQuery) -> None:
    text = "Внутри расширенной версии — больше практики и персональных разборов."
    await cb.message.edit_text(text, reply_markup=_inline_actions_kb())
    await cb.answer()


@router.callback_query(F.data == "premium:list")
async def premium_list(cb: types.CallbackQuery) -> None:
    await cb.answer()
    await cb.message.answer("Заявок пока нет.", reply_markup=_only_menu_kb())


@router.callback_query(F.data == "premium:apply")
async def premium_apply(cb: types.CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    await state.set_state(PremiumForm.WAIT_GOAL)
    await cb.message.answer(
        "Напишите цель одной короткой фразой (до 200 символов). Если передумали — /cancel.",
        reply_markup=_only_menu_kb(),
    )


@router.message(PremiumForm.WAIT_GOAL, F.text & ~F.text.startswith("/"))
async def premium_save_goal(message: types.Message, state: FSMContext) -> None:
    goal = (message.text or "").strip()
    # TODO: сохранить goal при необходимости
    await message.answer("Спасибо! Принял. Двигаемся дальше 👍")
    await _back_to_main_menu(message, state)


@router.message(PremiumForm.WAIT_GOAL, Command("cancel"))
async def premium_cancel(message: types.Message, state: FSMContext) -> None:
    await message.answer("Отменил. Ничего не сохранил.")
    await _back_to_main_menu(message, state)


@router.message(F.text == BACK_TO_MENU_TEXT)
async def premium_back_to_menu(message: types.Message, state: FSMContext) -> None:
    await _back_to_main_menu(message, state)
