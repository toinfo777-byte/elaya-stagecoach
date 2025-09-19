from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

router = Router(name="apply")

# Простое «состояние» без FSM
_WAIT_GOAL: set[int] = set()


def _apply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Оставить заявку")],
            [KeyboardButton(text="📣 В меню")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выбери действие…",
    )


@router.message(Command("apply"))
@router.message(F.text.lower().in_({"путь лидера", "🧭 путь лидера", "🧭 путь лидера (заявка)"}))
async def apply_entry(message: Message) -> None:
    txt = (
        "Путь лидера — индивидуальная траектория с фокусом на цели.\n"
        "Оставьте короткую заявку — вернусь с вопросами и предложениями."
    )
    await message.answer(txt, reply_markup=_apply_kb())


@router.message(F.text.lower() == "📝 оставить заявку")
async def apply_ask_goal(message: Message) -> None:
    _WAIT_GOAL.add(message.from_user.id)
    await message.answer(
        "Напишите цель одной короткой фразой (до 200 символов).\n"
        "Если передумали — отправьте /cancel.",
        reply_markup=_apply_kb(),
    )


@router.message(F.text.lower() == "/cancel")
async def apply_cancel(message: Message) -> None:
    _WAIT_GOAL.discard(message.from_user.id)
    await message.answer("Отменил. Что дальше?", reply_markup=_apply_kb())


# ловим любое текстовое сообщение как «цель», если человек в ожидании
@router.message(F.text & (F.from_user.id.func(lambda uid: uid in _WAIT_GOAL)))
async def apply_save_goal(message: Message) -> None:
    _WAIT_GOAL.discard(message.from_user.id)

    goal = (message.text or "").strip()
    # здесь можно сохранить goal в БД, если нужна персистентность
    # try: await repo.save_leader_path_goal(user_id=message.from_user.id, goal=goal) ...

    await message.answer("Спасибо! Принял. Двигаемся дальше 👍", reply_markup=_apply_kb())


# универсальная кнопка «В меню» (пусть отрабатывает ваш общий роутер)
@router.message(F.text.lower() == "📣 в меню")
async def back_to_menu(message: Message) -> None:
    # просто уберём локальную клавиатуру — дальше сработает ваш системный «В меню»
    await message.answer("Ок, вернулись в главное меню. Нажми нужную кнопку снизу.", reply_markup=ReplyKeyboardRemove())
