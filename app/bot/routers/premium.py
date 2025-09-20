from __future__ import annotations

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# попробуем взять общую клавиатуру меню, если она у тебя есть
try:
    from app.keyboards.menu import get_main_menu_kb  # type: ignore
except Exception:
    get_main_menu_kb = None  # fallback ниже

router = Router(name="premium")

BACK_TO_MENU_TEXT = "📎 В меню"


# --- FSM ---
class PremiumForm(StatesGroup):
    WAIT_GOAL = State()


# --- Клавиатуры ---
def _only_menu_kb() -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=BACK_TO_MENU_TEXT)]],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Открыть меню",
    )
    return kb


def _inline_actions_kb() -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="🔎 Что внутри", callback_data="premium:inside"),
            ],
            [
                types.InlineKeyboardButton(text="📝 Оставить заявку", callback_data="premium:apply"),
            ],
            [
                types.InlineKeyboardButton(text="📂 Мои заявки", callback_data="premium:list"),
            ],
        ]
    )
    return kb


def _main_menu_kb() -> types.ReplyKeyboardMarkup | None:
    # общий помощник: если есть твоя клавиатура — используем её
    if callable(get_main_menu_kb):
        try:
            return get_main_menu_kb()  # type: ignore[misc]
        except Exception:
            pass
    return None


async def _back_to_main_menu(message: types.Message, state: FSMContext | None = None) -> None:
    if state:
        await state.clear()
    menu_kb = _main_menu_kb()
    if menu_kb:
        await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=menu_kb)
    else:
        # запасной вариант — хотя бы оставить одну кнопку «В меню»
        await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=_only_menu_kb())


# --- Вход в раздел ---
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
    await message.answer(text, reply_markup=_only_menu_kb())
    await message.answer(" ", reply_markup=_inline_actions_kb())  # отдельным сообщением — только инлайн-кнопки


# --- Что внутри ---
@router.callback_query(F.data == "premium:inside")
async def premium_inside(cb: types.CallbackQuery) -> None:
    text = "Внутри расширенной версии — больше практики и персональных разборов."
    await cb.message.edit_text(text, reply_markup=_inline_actions_kb())
    await cb.answer()


# --- Мои заявки (плейсхолдер) ---
@router.callback_query(F.data == "premium:list")
async def premium_list(cb: types.CallbackQuery) -> None:
    await cb.answer()
    await cb.message.answer("Заявок пока нет.", reply_markup=_only_menu_kb())


# --- Оставить заявку ---
@router.callback_query(F.data == "premium:apply")
async def premium_apply(cb: types.CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    await state.set_state(PremiumForm.WAIT_GOAL)
    await cb.message.answer(
        "Напишите цель одной короткой фразой (до 200 символов). Если передумали — отправьте /cancel.",
        reply_markup=_only_menu_kb(),
    )


@router.message(PremiumForm.WAIT_GOAL, F.text & ~F.text.startswith("/"))
async def premium_save_goal(message: types.Message, state: FSMContext) -> None:
    goal = (message.text or "").strip()
    # здесь можно сохранить goal в БД
    # await repo.save_premium_goal(user_id=message.from_user.id, text=goal)

    await message.answer("Спасибо! Принял. Двигаемся дальше 👍")
    await _back_to_main_menu(message, state)


# --- Отмена ввода цели ---
@router.message(PremiumForm.WAIT_GOAL, Command("cancel"))
async def premium_cancel(message: types.Message, state: FSMContext) -> None:
    await message.answer("Отменил. Ничего не сохранил.")
    await _back_to_main_menu(message, state)


# --- Нижняя кнопка «В меню» ---
@router.message(F.text == BACK_TO_MENU_TEXT)
async def premium_back_to_menu(message: types.Message, state: FSMContext) -> None:
    await _back_to_main_menu(message, state)
