from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

router = Router(name="premium")

# Простая клавиатура раздела
def _premium_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔎 Что внутри")],
            [KeyboardButton(text="📝 Оставить заявку")],
            [KeyboardButton(text="📣 В меню")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выбери действие…",
    )


# мини «состояние» для заявки без FSM
_WAIT_PREMIUM_GOAL: set[int] = set()


@router.message(Command("premium"))
@router.message(F.text.lower().in_({"⭐ расширенная версия", "расширенная версия"}))
async def premium_entry(message: Message) -> None:
    txt = (
        "⭐ Расширенная версия\n\n"
        "• Ежедневный разбор и обратная связь\n"
        "• Разогрев голоса, дикции и внимания\n"
        "• Мини-кастинг и «путь лидера»\n\n"
        "Выберите действие:"
    )
    await message.answer(txt, reply_markup=_premium_kb())


@router.message(F.text.lower() == "🔎 что внутри")
async def premium_inside(message: Message) -> None:
    await message.answer(
        "Внутри расширенной версии — больше практики и персональных разборов.",
        reply_markup=_premium_kb(),
    )


@router.message(F.text.lower() == "📝 оставить заявку")
async def premium_ask_goal(message: Message) -> None:
    _WAIT_PREMIUM_GOAL.add(message.from_user.id)
    await message.answer(
        "Напишите цель одной короткой фразой (до 200 символов). "
        "Если передумали — отправьте /cancel.",
        reply_markup=_premium_kb(),
    )


@router.message(F.text.lower() == "/cancel")
async def premium_cancel(message: Message) -> None:
    _WAIT_PREMIUM_GOAL.discard(message.from_user.id)
    await message.answer("Отменил. Что дальше?", reply_markup=_premium_kb())


@router.message(F.text & (F.from_user.id.func(lambda uid: uid in _WAIT_PREMIUM_GOAL)))
async def premium_save_goal(message: Message) -> None:
    _WAIT_PREMIUM_GOAL.discard(message.from_user.id)
    goal = (message.text or "").strip()
    # здесь можно сохранить goal в БД

    # Благодарим и сразу убираем клавиатуру раздела,
    # чтобы пользователь вернулся в ваш общий «Меню»
    await message.answer(
        "Спасибо! Принял. Двигаемся дальше 👍",
        reply_markup=_premium_kb(),
    )


@router.message(F.text.lower() == "📣 в меню")
async def premium_back_to_menu(message: Message) -> None:
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=ReplyKeyboardRemove())
