# app/bot/handlers/feedback.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

# если у тебя класс состояний уже создан в app/bot/states.py — используем его
# (в твоём репозитории он назывался FeedbackStates с полем wait_phrase)
from app.bot.states import FeedbackStates

router = Router(name="feedback_v2")

# ---- callback constants
FB_FIRE = "fb_fire"
FB_OK = "fb_ok"
FB_NEUTRAL = "fb_neutral"
FB_PHRASE = "fb_phrase"


# ---- keyboard factory
def make_feedback_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура отзывов. ВАЖНО: порядок callback_data совпадает с порядком кнопок.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔥", callback_data=FB_FIRE),
                InlineKeyboardButton(text="👌", callback_data=FB_OK),
                InlineKeyboardButton(text="😐", callback_data=FB_NEUTRAL),
            ],
            [InlineKeyboardButton(text="✍️ 1 фраза", callback_data=FB_PHRASE)],
        ]
    )


# ---- emoji handlers (короткий отклик без смены состояния)
@router.callback_query(F.data == FB_FIRE)
async def on_fb_fire(cq: CallbackQuery) -> None:
    # Короткий toast-ответ; show_alert=False, чтобы не всплывало большим модальным окном
    await cq.answer("🔥 Принял. Спасибо!", show_alert=False)


@router.callback_query(F.data == FB_OK)
async def on_fb_ok(cq: CallbackQuery) -> None:
    await cq.answer("👌 Принял. Спасибо!", show_alert=False)


@router.callback_query(F.data == FB_NEUTRAL)
async def on_fb_neutral(cq: CallbackQuery) -> None:
    await cq.answer("😐 Принял. Спасибо!", show_alert=False)


# ---- phrase flow
@router.callback_query(F.data == FB_PHRASE)
async def on_fb_phrase(cq: CallbackQuery, state: FSMContext) -> None:
    # Сообщение в чат + переводим в состояние ожидания фразы
    await cq.message.answer(
        "Напишите одну короткую фразу об этом этюде. Если передумали — отправьте /cancel."
    )
    await state.set_state(FeedbackStates.wait_phrase)
    # обязательно закрываем спиннер callback’а
    await cq.answer()


# Пользователь прислал текст фразы
@router.message(FeedbackStates.wait_phrase, ~F.text.startswith("/"))
async def on_fb_phrase_text(msg: Message, state: FSMContext) -> None:
    phrase = (msg.text or "").strip()
    if not phrase:
        await msg.answer("Нужна короткая фраза — одно предложение. Попробуете ещё раз?")
        return

    # здесь можно сохранить фразу в БД/метрики; пока просто отвечаем
    await msg.answer("Супер, записал. Спасибо! 🎯")
    await state.clear()


# Отмена ввода фразы
@router.message(FeedbackStates.wait_phrase, Command("cancel"))
async def on_fb_phrase_cancel(msg: Message, state: FSMContext) -> None:
    await state.clear()
    await msg.answer("Ок, отменил ввод фразы.")


# (опционально) защита от случайных коллбеков нашего пространства имён
@router.callback_query(F.data.startswith("fb_"))
async def on_fb_unknown(cq: CallbackQuery) -> None:
    # Если вдруг прилетело что-то fb_* без хэндлера — просто вежливо ответим
    await cq.answer("Принял 👍", show_alert=False)
