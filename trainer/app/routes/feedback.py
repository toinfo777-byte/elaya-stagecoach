# trainer/app/routes/feedback.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from trainer.app.keyboards.main_menu import MAIN_MENU
from trainer.app.training_progress import register_feedback

router = Router(name="feedback")

USER_ID = 1  # один пользователь — достаточно


class FeedbackFlow(StatesGroup):
    emoji = State()
    text = State()


def _emoji_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="😀"),
                KeyboardButton(text="😐"),
                KeyboardButton(text="😔"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# Вход: команда /feedback и кнопка "📝 Отзыв о тренировке"
@router.message(Command("feedback"))
@router.message(F.text == "📝 Отзыв о тренировке")
async def start_feedback(message: Message, state: FSMContext) -> None:
    await state.set_state(FeedbackFlow.emoji)
    await message.answer(
        "Как тебе сегодняшняя тренировка?\n"
        "Выбери смайлик, который лучше всего описывает состояние.",
        reply_markup=_emoji_keyboard(),
    )


@router.message(FeedbackFlow.emoji)
async def handle_emoji(message: Message, state: FSMContext) -> None:
    emoji = (message.text or "").strip() or "😐"
    await state.update_data(emoji=emoji)
    await state.set_state(FeedbackFlow.text)

    await message.answer(
        "Если хочешь — напиши одну фразу о том, как это было.\n"
        "Например: «стало чуть спокойнее» или «сложно удерживать внимание».\n\n"
        "Если писать не хочется — можешь отправить что угодно.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(FeedbackFlow.text)
async def handle_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    emoji = data.get("emoji", "😐")
    comment = (message.text or "").strip() or "—"

    # сохраняем отзыв
    register_feedback(USER_ID, emoji=emoji, comment=comment)

    await message.answer(
        "Спасибо за отзыв. 💜\n"
        "Я учёл твою реакцию на тренировку.\n\n"
        "Возвращаю тебя в главное меню.",
        reply_markup=MAIN_MENU,
    )

    await state.clear()
