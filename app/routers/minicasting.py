# app/routers/minicasting.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.reply import main_menu_kb, BTN_CASTING
from app.storage.repo_extras import save_casting_session, save_feedback

router = Router(name="minicasting")

# одноразовая подсказка
MC_SEEN_FLAG = "seen_info_minicasting"

class MC(StatesGroup):
    q = State()          # проходим Q1..Q3
    wait_word = State()  # слово-ощущение после эмодзи/skip

QUESTIONS = {
    "q1": "Удержал ли 2 сек тишины перед фразой? (Да/Нет)",
    "q2": "Голос после паузы звучал ровнее? (Да/Нет)",
    "q3": "Что было труднее? (Пауза/Тембр/То же)",
}
Q_ORDER = ["q1", "q2", "q3"]

def _kb_yn_next():
    kb = InlineKeyboardBuilder()
    kb.button(text="Да",       callback_data="cast:ans:yes")
    kb.button(text="Нет",      callback_data="cast:ans:no")
    kb.button(text="Дальше",   callback_data="cast:next")
    kb.button(text="🏠 В меню", callback_data="go:menu")
    kb.adjust(2, 2)
    return kb.as_markup()

def _kb_q3():
    kb = InlineKeyboardBuilder()
    kb.button(text="Пауза",    callback_data="cast:ans:pause")
    kb.button(text="Тембр",    callback_data="cast:ans:tembr")
    kb.button(text="То же",    callback_data="cast:ans:same")
    kb.button(text="Дальше",   callback_data="cast:next")
    kb.button(text="🏠 В меню", callback_data="go:menu")
    kb.adjust(3, 2)
    return kb.as_markup()

def _kb_feedback():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔥", callback_data="cast:rate:fire")
    kb.button(text="👌", callback_data="cast:rate:ok")
    kb.button(text="😐", callback_data="cast:rate:meh")
    kb.button(text="Пропустить", callback_data="cast:skip")
    kb.button(text="🏠 В меню",  callback_data="go:menu")
    kb.adjust(3, 2)
    return kb.as_markup()

# ── Публичный entry (единое имя) ─────────────────────────────────────────────
async def minicasting_entry(message: Message, state: FSMContext) -> None:
    await state.set_state(MC.q)
    await state.update_data(idx=0, answers={})
    data = await state.get_data()
    if not data.get(MC_SEEN_FLAG):
        await message.answer(
            "ℹ️ Мини-кастинг: короткий чек — пауза, тембр, ощущение. "
            "На выходе — 1 рекомендация и круг тренировки."
        )
        await state.update_data(**{MC_SEEN_FLAG: True})
    await message.answer(
        "Это мини-кастинг: 2–3 мин. Отвечай коротко. Готов?",
        reply_markup=_kb_yn_next()
    )

# alias совместимости
start_minicasting = minicasting_entry

# ── входы из разных мест ──────────────────────────────────────────────────────
@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def start_by_btn(msg: Message, state: FSMContext):
    await minicasting_entry(msg, state)

@router.message(StateFilter("*"), Command("casting"))
async def start_by_cmd(msg: Message, state: FSMContext):
    await minicasting_entry(msg, state)

@router.callback_query(StateFilter("*"), F.data == "go:casting")
async def start_by_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await minicasting_entry(cb.message, state)

# общий ACK для всех «cast:*» чтобы не висела крутилка
@router.callback_query(F.data.startswith("cast:"))
async def _ack_any(cb: CallbackQuery):
    await cb.answer(cache_time=1)

# ── ход вопросов ──────────────────────────────────────────────────────────────
@router.callback_query(StateFilter(MC.q), F.data.in_({"cast:ans:yes", "cast:ans:no", "cast:next"}))
async def on_answer(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    idx = int(data.get("idx", 0))
    key = Q_ORDER[idx] if idx < len(Q_ORDER) else None
    answers = dict(data.get("answers", {}))
    # запишем ответ, если был
    if cb.data != "cast:next" and key:
        answers[key] = cb.data.split(":")[-1]
    # двигаемся
    idx += 1
    if idx < len(Q_ORDER):
        await state.update_data(idx=idx, answers=answers)
        next_key = Q_ORDER[idx]
        if next_key == "q3":
            await cb.message.edit_text(QUESTIONS[next_key], reply_markup=_kb_q3())
        else:
            await cb.message.edit_text(QUESTIONS[next_key], reply_markup=_kb_yn_next())
        return

    # финал: краткий совет + фидбек
    pause_flag = (answers.get("q1") == "no") or (answers.get("q2") == "no")
    tip = "Точка роста: не давай паузе проваливаться." if pause_flag else "Отлично! Держи курс и темп."
    await cb.message.edit_text(f"Итог: {tip}")
    await cb.message.answer(
        "Оцени опыт 🔥/👌/😐 и добавь 1 слово-ощущение (необязательно).",
        reply_markup=_kb_feedback()
    )
    # сохраняем сессию
    try:
        await save_casting_session(
            user_id=cb.from_user.id,
            answers=[answers.get("q1"), answers.get("q2"), answers.get("q3")],
            result=("pause" if pause_flag else "ok")
        )
    except Exception:
        pass
    await state.set_state(MC.wait_word)

@router.callback_query(StateFilter(MC.q), F.data.in_({"cast:ans:pause", "cast:ans:tembr", "cast:ans:same"}))
async def on_q3(cb: CallbackQuery, state: FSMContext):
    # записываем ответ для q3 и двигаем как «next»
    data = await state.get_data()
    answers = dict(data.get("answers", {}))
    answers["q3"] = cb.data.split(":")[-1]
    await state.update_data(answers=answers)
    # переиспользуем логику next
    await on_answer(cb, state)

# ── фидбек: эмодзи или скип → слово (необяз.) → меню ─────────────────────────
@router.callback_query(StateFilter(MC.wait_word), F.data.startswith("cast:rate:"))
async def on_rate(cb: CallbackQuery, state: FSMContext):
    emoji = cb.data.split(":")[-1]  # fire|ok|meh
    await state.update_data(_mc_emoji=emoji)
    # сразу сохраним эмодзи (фраза может не прийти)
    try:
        await save_feedback(cb.from_user.id, emoji=emoji, phrase=None)
    except Exception:
        pass
    await cb.message.answer(
        "Принял. Можешь одним словом дописать ощущение (до 140 симв) "
        "или нажми «🏠 В меню».",
        reply_markup=_kb_feedback()
    )

@router.callback_query(StateFilter(MC.wait_word), F.data == "cast:skip")
async def on_skip(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer("Ок, вернёмся завтра. Возвращаю в меню.", reply_markup=main_menu_kb())

@router.message(StateFilter(MC.wait_word), F.text)
async def on_word(msg: Message, state: FSMContext):
    data = await state.get_data()
    emoji = data.get("_mc_emoji", None)
    phrase = (msg.text or "").strip()[:140]
    try:
        await save_feedback(msg.from_user.id, emoji=emoji or "👌", phrase=phrase)
    except Exception:
        pass
    await state.clear()
    await msg.answer("Спасибо! Записал. Возвращаю в меню.", reply_markup=main_menu_kb())

__all__ = ["router", "minicasting_entry", "start_minicasting"]
