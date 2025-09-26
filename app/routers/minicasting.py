# app/routers/minicasting.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.reply import main_menu_kb, BTN_CASTING
from app.storage.repo_extras import save_casting_session, save_feedback

router = Router(name="minicasting")


class MiniCasting(StatesGroup):
    q = State()         # шаг вопроса (0..len)
    answers = State()   # список ответов
    feedback = State()  # ждём эмодзи/слово


QUESTIONS = [
    "Удержал ли 2 сек тишины перед фразой? (Да/Нет)",
    "Голос после паузы звучал ровнее? (Да/Нет)",
    "Что было труднее? (Пауза/Тембр/То же)",
    "Лёгкость дыхания по ощущениям? (Да/Нет)",
    "Хочешь повторить круг сейчас? (Да/Нет)",
]


def yn_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Да",      callback_data="mini:yes")
    kb.button(text="Нет",     callback_data="mini:no")
    kb.button(text="Дальше",  callback_data="mini:next")
    kb.button(text="В меню",  callback_data="mini:menu")
    kb.adjust(2, 2)
    return kb.as_markup()


async def _start_minicasting_core(msg: Message, state: FSMContext):
    """Единая точка входа (used by: кнопка, /casting, диплинк, entrypoints)."""
    await state.set_state(MiniCasting.q)
    await state.update_data(q=0, answers=[])
    await msg.answer(
        "Это мини-кастинг: 2–3 мин. Отвечай коротко. Готов?",
        reply_markup=yn_kb(),
    )


# ── Entry-пойнты (кнопка + команда) ────────────────────────────────────────────

@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def _start_from_button(msg: Message, state: FSMContext):
    await _start_minicasting_core(msg, state)


@router.message(StateFilter("*"), Command("casting"))
async def _start_from_command(msg: Message, state: FSMContext):
    await _start_minicasting_core(msg, state)


# ── Ход вопросов ───────────────────────────────────────────────────────────────

@router.callback_query(MiniCasting.q, F.data.startswith("mini:"))
async def on_answer(cb: CallbackQuery, state: FSMContext):
    # мгновенно гасим «часики»
    await cb.answer()

    data = await state.get_data()
    q = data["q"]
    answers = data["answers"]

    if cb.data == "mini:menu":
        await state.clear()
        return await cb.message.answer("В меню.", reply_markup=main_menu_kb())

    if cb.data in {"mini:yes", "mini:no"}:
        answers.append(cb.data.split(":")[1])

    # следующий вопрос
    q += 1
    if q <= len(QUESTIONS):
        await state.update_data(q=q, answers=answers)
        return await cb.message.edit_text(QUESTIONS[q - 1], reply_markup=yn_kb())

    # финал вопросов → короткий совет + запрос фидбэка
    tip = (
        "Точка роста: не давай паузе проваливаться."
        if answers[:2].count("no") >= 1 else
        "Отлично! Держи курс и темп."
    )
    await cb.message.edit_text(f"Итог: {tip}")

    kb = InlineKeyboardBuilder()
    for emo, code in (("🔥", "fire"), ("👌", "ok"), ("😐", "meh")):
        kb.button(text=emo, callback_data=f"fb:{code}")
    kb.button(text="Пропустить", callback_data="mc:skip")
    kb.adjust(3, 1)
    await cb.message.answer(
        "Оцени опыт 🔥/👌/😐 и добавь 1 слово-ощущение (необязательно).",
        reply_markup=kb.as_markup()
    )
    await state.set_state(MiniCasting.feedback)

    # сохраняем сессию
    await save_casting_session(
        cb.from_user.id,
        answers=answers,
        result=("pause" if "no" in answers[:2] else "ok"),
    )


# ── Фидбэк: эмодзи/слово/пропуск ───────────────────────────────────────────────

@router.callback_query(MiniCasting.feedback, F.data == "mc:skip")
async def mc_skip(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    await cb.message.answer("Ок, вернёмся завтра. Возвращаю в меню.", reply_markup=main_menu_kb())


@router.callback_query(MiniCasting.feedback, F.data.startswith("fb:"))
async def on_fb_emoji(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    emoji_code = cb.data.split(":", 1)[1]  # fire|ok|meh
    # сохраняем эмодзи сразу (фраза может не прийти)
    await save_feedback(cb.from_user.id, emoji=emoji_code, phrase=None)
    await cb.message.answer(
        "Принял эмодзи. Можешь одним словом дописать ощущение (до 140 симв) или напиши «/menu»."
    )
    # остаёмся в MiniCasting.feedback — ждём текст


# принимаем ЛЮБОЙ текст в состоянии feedback (без F.text фильтра),
# чтобы не «молчать» на стикеры и т.п. — но сохраняем только text
@router.message(MiniCasting.feedback)
async def on_fb_phrase(msg: Message, state: FSMContext):
    phrase = (msg.text or "").strip()[:140] if msg.text else ""
    if phrase:
        # если фраза есть — добьём запись
        await save_feedback(msg.from_user.id, emoji="text", phrase=phrase)
    await state.clear()
    await msg.answer("Спасибо! Записал. Возвращаю в меню.", reply_markup=main_menu_kb())


# ── Публичные entry-алиасы для диплинков/entrypoints ──────────────────────────

async def minicasting_entry(message: Message, state: FSMContext) -> None:
    """Каноническая точка входа (используйте в диплинках и entrypoints)."""
    await _start_minicasting_core(message, state)


# Исторический алиас: некоторые модули импортируют start_minicasting
async def start_minicasting(message: Message, state: FSMContext) -> None:
    await minicasting_entry(message, state)


__all__ = ["router", "minicasting_entry", "start_minicasting"]
