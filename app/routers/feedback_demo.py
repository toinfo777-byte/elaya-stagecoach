# app/routers/feedback_demo.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates

router = Router(name="feedback_demo")


# --- keyboard ---------------------------------------------------------------

def _feedback_kb() -> InlineKeyboardMarkup:
    """
    Мини-клавиатура оценок + «✍ 1 фраза».
    Префикс callback_data: demo_fb:...
    """
    rows = [
        [
            InlineKeyboardButton(text="🔥", callback_data="demo_fb:rate:hot"),
            InlineKeyboardButton(text="👌", callback_data="demo_fb:rate:ok"),
            InlineKeyboardButton(text="😐", callback_data="demo_fb:rate:meh"),
        ],
        [InlineKeyboardButton(text="✍ 1 фраза", callback_data="demo_fb:phrase")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# --- entry point ------------------------------------------------------------

@router.message(F.text.in_({"/feedback", "/fb", "отзыв"}))
async def feedback_entry(msg: Message, state: FSMContext) -> None:
    """Команда для показа клавиатуры где угодно."""
    # на всякий — сбросим «ожидание фразы», если юзер начал с команды
    if await state.get_state() == FeedbackStates.wait_phrase:
        await state.clear()

    await msg.answer("Как прошёл этот эпизод? Оцените или оставьте короткий отзыв:",
                     reply_markup=_feedback_kb())


# --- rate buttons -----------------------------------------------------------

@router.callback_query(F.data.startswith("demo_fb:rate:"))
async def feedback_rate(cb: CallbackQuery) -> None:
    """
    Обработка нажатий 🔥/👌/😐.
    Здесь можно положить в БД/метрики (cb.from_user.id, значение).
    """
    _, _, value = cb.data.partition("demo_fb:rate:")
    # TODO: save rating (cb.from_user.id, value)

    # короткий ответ во всплывашке и аккуратный reply
    await cb.answer("Сохранено, спасибо!")
    if cb.message:
        await cb.message.reply("Принял 👍")


# --- phrase flow ------------------------------------------------------------

@router.callback_query(F.data == "demo_fb:phrase")
async def feedback_phrase_start(cb: CallbackQuery, state: FSMContext) -> None:
    """
    Нажата «✍ 1 фраза» — просим текст и ставим FSM-состояние.
    """
    await cb.answer()  # скрыть "часики"
    await state.set_state(FeedbackStates.wait_phrase)
    await cb.message.reply(
        "Напишите одну короткую фразу (до 120 символов).\n"
        "Если передумали — отправьте /cancel."
    )


@router.message(FeedbackStates.wait_phrase, F.text)
async def feedback_phrase_save(msg: Message, state: FSMContext) -> None:
    """
    Принимаем одну короткую фразу, валидируем, «сохраняем», выходим из состояния.
    """
    text = (msg.text or "").strip()
    if not text or len(text) > 120:
        await msg.reply("Пожалуйста, одна короткая фраза (до 120 символов).")
        return

    # TODO: save phrase (msg.from_user.id, text)

    await state.clear()
    await msg.reply("Готово! Сохранил 👍")


@router.message(FeedbackStates.wait_phrase, F.text == "/cancel")
async def feedback_phrase_cancel(msg: Message, state: FSMContext) -> None:
    await state.clear()
    await msg.reply("Ок, отменил. Можете открыть меню: /menu")
