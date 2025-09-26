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


# ── FSM ────────────────────────────────────────────────────────────────────────
class MiniCasting(StatesGroup):
    q = State()          # этап коротких «Да/Нет»
    feedback = State()   # этап финального отзыва (эмодзи/слово)


# ── Контент/клавиатуры ────────────────────────────────────────────────────────
QUESTIONS = [
    "Удержал(а) ли 2 сек тишины перед фразой? (Да/Нет)",
    "Голос после паузы звучал ровнее? (Да/Нет)",
    "Что было труднее? (Пауза/Тембр/То же) — отвечай Да/Нет по ощущению",
    "Лёгкость дыхания по ощущениям? (Да/Нет)",
    "Хочешь повторить круг сейчас? (Да/Нет)",
]

def _yn_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="mini:yes")
    kb.button(text="Нет", callback_data="mini:no")
    kb.button(text="Дальше", callback_data="mini:next")
    kb.button(text="🏠 В меню", callback_data="mini:menu")
    kb.adjust(2, 2)
    return kb.as_markup()

def _mc_feedback_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔥", callback_data="mc:rate:fire")
    kb.button(text="👌", callback_data="mc:rate:ok")
    kb.button(text="😐", callback_data="mc:rate:meh")
    kb.button(text="Пропустить", callback_data="mc:rate:skip")
    kb.button(text="🏠 В меню", callback_data="go:menu")
    kb.adjust(3, 1, 1)
    return kb.as_markup()


# ── Публичные входы ───────────────────────────────────────────────────────────
async def minicasting_entry(message: Message, state: FSMContext):
    """Показать/запустить мини-кастинг (для диплинков и entrypoints)."""
    await state.set_state(MiniCasting.q)
    await state.update_data(q=0, answers=[])
    await message.answer("Это мини-кастинг: 2–3 мин. Отвечай коротко. Готов(а)?", reply_markup=_yn_kb())

# совместимость со старыми импортами
start_minicasting = minicasting_entry

@router.message(StateFilter("*"), F.text == BTN_CASTING)
async def start_minicasting_btn(msg: Message, state: FSMContext):
    await minicasting_entry(msg, state)

@router.message(StateFilter("*"), Command("casting"))
async def start_minicasting_cmd(msg: Message, state: FSMContext):
    await minicasting_entry(msg, state)

@router.callback_query(StateFilter("*"), F.data == "go:casting")
async def start_minicasting_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await minicasting_entry(cb.message, state)


# ── Основной опрос Да/Нет ─────────────────────────────────────────────────────
@router.callback_query(MiniCasting.q, F.data.startswith("mini:"))
async def mc_yes_no_next(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    data = await state.get_data()
    q_idx: int = data.get("q", 0)
    answers: list[str] = data.get("answers", [])

    if cb.data == "mini:menu":
        await state.clear()
        await cb.message.answer("Готово! Открываю меню.", reply_markup=main_menu_kb())
        return

    if cb.data in {"mini:yes", "mini:no"}:
        answers.append(cb.data.split(":")[1])

    q_idx += 1
    if q_idx <= len(QUESTIONS):
        await state.update_data(q=q_idx, answers=answers)
        await cb.message.edit_text(QUESTIONS[q_idx - 1], reply_markup=_yn_kb())
        return

    # финал: краткий совет + запрос отзыва
    tip = (
        "Точка роста: не давай паузе проваливаться."
        if answers[:2].count("no") >= 1 else
        "Отлично! Держи курс и темп."
    )
    await cb.message.edit_text(f"Итог: {tip}")
    await cb.message.answer(
        "Оцени опыт 🔥/👌/😐 и (по желанию) добавь 1 слово-ощущение.",
        reply_markup=_mc_feedback_kb(),
    )
    await state.set_state(MiniCasting.feedback)

    # безопасно фиксируем сессию (не падаем, если БД недоступна)
    try:
        await save_casting_session(
            user_id=cb.from_user.id,
            answers=answers,
            result=("pause" if "no" in answers[:2] else "ok"),
        )
    except Exception:
        pass


# ── Финальный отзыв (эмодзи/пропуск/слово) ────────────────────────────────────
@router.callback_query(MiniCasting.feedback, F.data.startswith("mc:rate:"))
async def mc_feedback_rate(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    rate = cb.data.split(":")[-1]  # fire|ok|meh|skip

    # сохраняем только, если не skip
    if rate != "skip":
        try:
            await save_feedback(cb.from_user.id, emoji=rate, phrase=None)
        except Exception:
            pass

    await state.clear()
    await cb.message.answer("Спасибо! Записал. Возвращаю в меню.", reply_markup=main_menu_kb())


@router.message(MiniCasting.feedback)  # любое текстовое «слово-ощущение»
async def mc_feedback_word(msg: Message, state: FSMContext):
    phrase = (msg.text or "").strip()[:140] if msg.text else ""
    if phrase:
        try:
            await save_feedback(msg.from_user.id, emoji=None, phrase=phrase)
        except Exception:
            pass
    await state.clear()
    await msg.answer("Спасибо! Записал. Возвращаю в меню.", reply_markup=main_menu_kb())


__all__ = ["router", "minicasting_entry", "start_minicasting", "start_minicasting_cmd"]
