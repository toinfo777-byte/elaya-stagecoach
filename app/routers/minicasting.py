# app/routers/minicasting.py
from __future__ import annotations

import json
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.keyboards.reply import main_menu_kb, BTN_CASTING
# ВАЖНО: единый источник – app.storage.repo
from app.storage.repo import save_casting_session, save_feedback, log_progress_event

router = Router(name="minicasting")


# ===========================
# Клавиатуры (inline)
# ===========================
def kb_start() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="mc:s0:yes"),
         InlineKeyboardButton(text="Нет", callback_data="mc:s0:no")],
        [InlineKeyboardButton(text="Дальше", callback_data="mc:s0:next")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])


def kb_q1() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="mc:s1:yes"),
         InlineKeyboardButton(text="Нет", callback_data="mc:s1:no")],
        [InlineKeyboardButton(text="Дальше", callback_data="mc:s1:next"),
         InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])


def kb_q2() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="mc:s2:yes"),
         InlineKeyboardButton(text="Нет", callback_data="mc:s2:no")],
        [InlineKeyboardButton(text="Дальше", callback_data="mc:s2:next"),
         InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])


def kb_q3() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пауза", callback_data="mc:s3:pause"),
         InlineKeyboardButton(text="Тембр", callback_data="mc:s3:timbre"),
         InlineKeyboardButton(text="То же", callback_data="mc:s3:same")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])


def kb_rate() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥", callback_data="mc:rate:fire"),
         InlineKeyboardButton(text="👌", callback_data="mc:rate:ok"),
         InlineKeyboardButton(text="😐", callback_data="mc:rate:meh")],
        [InlineKeyboardButton(text="Пропустить", callback_data="mc:rate:skip")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])


# ===========================
# FSM
# ===========================
class MC(StatesGroup):
    wait_word = State()  # ждём одно слово-ощущение после эмодзи


# ===========================
# Entry (единая точка входа)
# ===========================
async def start_minicasting(target: Message | CallbackQuery, state: FSMContext) -> None:
    """
    Единая точка входа (из message или из callback): старт мини-кастинга.
    """
    if isinstance(target, CallbackQuery):
        await target.answer()
        m = target.message
    else:
        m = target

    await state.clear()
    await state.update_data(ans=[])  # будем копить ответы Q1/Q2
    await m.answer(
        "🎭 Мини-кастинг: короткий чек — пауза, тембр, ощущение. "
        "На выходе — 1 рекомендация и круг тренировки."
    )
    await m.answer("Это мини-кастинг: 2–3 мин. Отвечай коротко. Готов?", reply_markup=kb_start())


# Старт по кнопке из ReplyKeyboard (если используете) и по команде /casting
@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def start_minicasting_btn(msg: Message, state: FSMContext):
    await start_minicasting(msg, state)


@router.message(StateFilter("*"), Command("casting"))
async def start_minicasting_cmd(msg: Message, state: FSMContext):
    await start_minicasting(msg, state)


# ===========================
# Шаги опроса
# ===========================
@router.callback_query(StateFilter("*"), F.data.in_({"mc:s0:yes", "mc:s0:no", "mc:s0:next"}))
async def mc_step_1(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await cq.message.answer("Q1. Удержал ли 2 сек тишины перед фразой?", reply_markup=kb_q1())


@router.callback_query(StateFilter("*"), F.data.startswith("mc:s1:"))
async def mc_step_2(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    ans = cq.data.split(":")[-1]  # yes|no|next
    data = await state.get_data()
    answers = list(data.get("ans", []))
    if ans in {"yes", "no"}:
        answers.append(ans)
        await state.update_data(ans=answers)

    await cq.message.answer("Q2. Голос после паузы звучал ровнее?", reply_markup=kb_q2())


@router.callback_query(StateFilter("*"), F.data.startswith("mc:s2:"))
async def mc_step_3(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    ans = cq.data.split(":")[-1]  # yes|no|next
    data = await state.get_data()
    answers = list(data.get("ans", []))
    if ans in {"yes", "no"}:
        answers.append(ans)
        await state.update_data(ans=answers)

    await cq.message.answer("Q3. Что было труднее?", reply_markup=kb_q3())


@router.callback_query(StateFilter("*"), F.data.startswith("mc:s3:"))
async def mc_summary(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    diff = cq.data.split(":")[-1]  # pause|timbre|same
    data = await state.get_data()
    answers: list[str] = list(data.get("ans", []))

    tip = (
        "Точка роста: не давай паузе проваливаться."
        if answers[:2].count("no") >= 1
        else "Отлично! Держи курс и темп."
    )

    await cq.message.answer(f"Итог: {tip}")
    await cq.message.answer(
        "Оцени опыт 🔥/👌/😐 и добавь 1 слово-ощущение (необязательно).",
        reply_markup=kb_rate(),
    )

    # сохранить сессию (единый контракт repo: tg_id + payload:str)
    try:
        payload = json.dumps({
            "answers": answers,
            "diff": diff,
            "result": "pause" if "no" in answers[:2] else "ok",
        }, ensure_ascii=False)
        await save_casting_session(tg_id=cq.from_user.id, payload=payload)
        await log_progress_event(tg_id=cq.from_user.id, kind="minicasting")
    except Exception:
        # не роняем поток при ошибке записи
        pass


# ===========================
# Фидбэк (эмодзи + слово)
# ===========================
_EMOJI_TO_RATING = {"fire": 3, "ok": 2, "meh": 1}

@router.callback_query(StateFilter("*"), F.data.startswith("mc:rate:"))
async def mc_rate(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    rate = cq.data.split(":")[-1]  # fire|ok|meh|skip

    if rate == "skip":
        await state.clear()
        await cq.message.answer("Ок, вернёмся завтра. Возвращаю в меню.", reply_markup=main_menu_kb())
        return

    await state.update_data(emoji=rate)
    await state.set_state(MC.wait_word)
    await cq.message.answer(
        "Принял эмодзи. Можешь одним словом дописать ощущение (до 140 симв) или напиши «/menu»."
    )


@router.message(MC.wait_word)
async def mc_word(msg: Message, state: FSMContext):
    data = await state.get_data()
    emoji = str(data.get("emoji", "ok"))
    phrase = (msg.text or "").strip()[:140] if msg.text else ""

    try:
        rating = _EMOJI_TO_RATING.get(emoji, None)
        text = (f"emoji={emoji}; " + phrase).strip()
        await save_feedback(tg_id=msg.from_user.id, text=text, rating=rating)
    except Exception:
        pass

    await state.clear()
    await msg.answer("Спасибо! Записал. Возвращаю в меню.", reply_markup=main_menu_kb())


# Публичные экспортируемые имена
mc_router = router
__all__ = ["router", "mc_router", "start_minicasting", "start_minicasting_cmd"]
