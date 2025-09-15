# app/routers/feedback_any.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.bot.states import FeedbackStates

router = Router(name="feedback_any")


# === (необязательно) показать клавиатуру по команде =========================
def _ratings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔥", callback_data="fb:rate:hot"),
                InlineKeyboardButton(text="👌", callback_data="fb:rate:ok"),
                InlineKeyboardButton(text="😐", callback_data="fb:rate:meh"),
            ],
            [InlineKeyboardButton(text="✍ 1 фраза", callback_data="fb:phrase")],
        ]
    )

@router.message(F.text.in_({"/feedback", "/fb", "отзыв"}))
async def feedback_entry(msg: Message, state: FSMContext) -> None:
    if await state.get_state() == FeedbackStates.wait_phrase:
        await state.clear()
    await msg.answer("Как прошёл эпизод? Оцените или оставьте короткий отзыв:", reply_markup=_ratings_kb())


# === оценки (🔥/👌/😐), поддержка префиксов fb:* И demo_fb:* ==================
@router.callback_query(F.data.regexp(r"^(?:fb|demo_fb):rate:(.+)$"))
async def on_rate(cb: CallbackQuery) -> None:
    value = cb.match.group(1)  # 'hot' | 'ok' | 'meh'
    # TODO: тут сохраняем значение (cb.from_user.id, value)
    await cb.answer("Сохранено!")
    if cb.message:
        await cb.message.reply("Принял 👍")


# === старт ввода фразы (поддержка fb:phrase И demo_fb:phrase) ================
@router.callback_query(F.data.in_({"fb:phrase", "demo_fb:phrase"}))
async def on_phrase_start(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    await state.set_state(FeedbackStates.wait_phrase)
    await cb.message.reply(
        "Напишите одну короткую фразу (до 120 символов).\n"
        "Если передумали — отправьте /cancel."
    )


# === приём фразы =============================================================
@router.message(FeedbackStates.wait_phrase, F.text)
async def on_phrase_save(msg: Message, state: FSMContext) -> None:
    text = (msg.text or "").strip()
    if not text or len(text) > 120:
        await msg.reply("Пожалуйста, одна короткая фраза (до 120 символов).")
        return

    # TODO: сохраняем (msg.from_user.id, text)
    await state.clear()
    await msg.reply("Готово! Сохранил 👍")


# === отмена фразы ============================================================
@router.message(FeedbackStates.wait_phrase, F.text == "/cancel")
async def on_phrase_cancel(msg: Message, state: FSMContext) -> None:
    await state.clear()
    await msg.reply("Ок, отменил. Можно вернуться в меню: /menu")
