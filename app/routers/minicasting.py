from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.reply import main_menu_kb, BTN_CASTING
from app.storage.repo_extras import (
    save_casting_session, save_feedback, log_progress_event
)

router = Router(name="minicasting")


# === Состояния ==============================================================

class MiniCasting(StatesGroup):
    q = State()
    feedback = State()


# === Вопросы и клавиатуры ===================================================

QUESTIONS = [
    "Удержал ли 2 сек тишины перед фразой? (Да/Нет)",
    "Голос после паузы звучал ровнее? (Да/Нет)",
    "Что было труднее? (Пауза/Тембр/То же)",
    "Лёгкость дыхания по ощущениям? (Да/Нет)",
    "Хочешь повторить круг сейчас? (Да/Нет)",
]


def _yn_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="mini:yes")
    kb.button(text="Нет", callback_data="mini:no")
    kb.button(text="Дальше", callback_data="mini:next")
    kb.button(text="🏠 В меню", callback_data="mc:skip")
    kb.adjust(2, 2)
    return kb.as_markup()


def _feedback_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔥", callback_data="fb:fire")
    kb.button(text="👌", callback_data="fb:ok")
    kb.button(text="😐", callback_data="fb:meh")
    kb.button(text="Пропустить", callback_data="mc:skip")
    kb.adjust(3, 1)
    return kb.as_markup()


# === Публичные входы ========================================================

async def minicasting_entry(message: Message, state: FSMContext):
    """Единый старт мини-кастинга (кнопка/команда/диплинк)."""
    await state.set_state(MiniCasting.q)
    await state.update_data(q=0, answers=[], emoji=None)
    await message.answer("Это мини-кастинг: 2–3 мин. Отвечай коротко. Готов?", reply_markup=_yn_kb())


# алиас для совместимости
start_minicasting = minicasting_entry


@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def start_minicasting_by_button(msg: Message, state: FSMContext):
    await minicasting_entry(msg, state)


@router.message(StateFilter("*"), Command("casting", "minicasting"))
async def start_minicasting_cmd(msg: Message, state: FSMContext):
    await minicasting_entry(msg, state)


# === Основной опрос =========================================================

@router.callback_query(StateFilter(MiniCasting.q), F.data.startswith("mini:"))
async def on_answer(cb: CallbackQuery, state: FSMContext):
    await cb.answer()

    data = await state.get_data()
    q = int(data.get("q", 0))
    answers: list = data.get("answers", [])

    if cb.data in {"mini:yes", "mini:no"}:
        answers.append(cb.data.split(":")[1])

    if cb.data == "mini:next":
        # просто перейти дальше, не добавляя ответа
        pass

    # «В меню» во время опроса — через mc:skip
    # шаг вперёд
    q += 1

    if q <= len(QUESTIONS):
        await state.update_data(q=q, answers=answers)
        await cb.message.edit_text(QUESTIONS[q - 1], reply_markup=_yn_kb())
    else:
        # мини-резюме
        tip = "Точка роста: не давай паузе проваливаться." if answers[:2].count("no") >= 1 else "Отлично! Держи курс и темп."
        await cb.message.edit_text(f"Итог: {tip}")
        await cb.message.answer(
            "Оцени опыт 🔥/👌/😐 и добавь 1 слово-ощущение (необязательно).",
            reply_markup=_feedback_kb()
        )
        await state.set_state(MiniCasting.feedback)
        # сохранить сессию
        try:
            await save_casting_session(cb.from_user.id, answers=answers, result=("pause" if "no" in answers[:2] else "ok"))
        except Exception:
            pass  # не ломаем UX


# === Отзыв/финал ============================================================

@router.callback_query(StateFilter(MiniCasting.feedback), F.data == "mc:skip")
async def mc_skip(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    # зачтём событие «minicasting»
    try:
        await log_progress_event(cb.from_user.id, kind="minicasting", level=None)
    except Exception:
        pass
    await state.clear()
    await cb.message.answer("Ок, вернёмся завтра. Возвращаю в меню.", reply_markup=main_menu_kb())


@router.callback_query(StateFilter(MiniCasting.feedback), F.data.startswith("fb:"))
async def on_fb_emoji(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    emoji = cb.data.split(":", 1)[1]
    await state.update_data(emoji=emoji)
    await cb.message.answer("Принял эмодзи. Можешь одним словом дописать ощущение (до 140 симв) или напиши «/menu».")


@router.message(StateFilter(MiniCasting.feedback))
async def on_fb_phrase(msg: Message, state: FSMContext):
    data = await state.get_data()
    emoji = data.get("emoji")
    phrase = (msg.text or "")[:140] if msg.text else None
    try:
        await save_feedback(msg.from_user.id, emoji=emoji, phrase=phrase)
    except Exception:
        pass
    # зачтём событие «minicasting»
    try:
        await log_progress_event(msg.from_user.id, kind="minicasting", level=None)
    except Exception:
        pass

    await state.clear()
    await msg.answer("Спасибо! Записал. Возвращаю в меню.", reply_markup=main_menu_kb())


# === Экспорт ================================================================

__all__ = ["router", "minicasting_entry", "start_minicasting"]
