from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from app.keyboards.reply import main_menu_kb
from app.storage.repo_extras import save_casting_session, save_feedback

# единый роутер этого модуля
mc_router = Router(name="minicasting")
router = mc_router  # совместимость с импортом r_minicasting.router

# ── keyboards ────────────────────────────────────────────────────────────────
def kb_mc_start() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да",     callback_data="mc:s0:yes"),
         InlineKeyboardButton(text="Нет",    callback_data="mc:s0:no")],
        [InlineKeyboardButton(text="Дальше", callback_data="mc:s0:next")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def kb_mc_q1() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да",     callback_data="mc:s1:yes"),
         InlineKeyboardButton(text="Нет",    callback_data="mc:s1:no")],
        [InlineKeyboardButton(text="Дальше", callback_data="mc:s1:next"),
         InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def kb_mc_q2() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да",     callback_data="mc:s2:yes"),
         InlineKeyboardButton(text="Нет",    callback_data="mc:s2:no")],
        [InlineKeyboardButton(text="Дальше", callback_data="mc:s2:next"),
         InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def kb_mc_q3() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пауза",  callback_data="mc:s3:pause"),
         InlineKeyboardButton(text="Тембр",  callback_data="mc:s3:timbre"),
         InlineKeyboardButton(text="То же",  callback_data="mc:s3:same")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def kb_mc_rate() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥", callback_data="mc:rate:fire"),
         InlineKeyboardButton(text="👌", callback_data="mc:rate:ok"),
         InlineKeyboardButton(text="😐", callback_data="mc:rate:meh")],
        [InlineKeyboardButton(text="Пропустить", callback_data="mc:rate:skip")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

# ── FSM: слово-ощущение ─────────────────────────────────────────────────────
class McState(StatesGroup):
    wait_text = State()

# ── PUBLIC ENTRY ─────────────────────────────────────────────────────────────
async def start_minicasting(message_or_cq: Message | CallbackQuery, state: FSMContext):
    """
    Публичный вход: запускает мини-кастинг из message/callback.
    Экспортируй и используй в help/entrypoints/deeplink.
    """
    if isinstance(message_or_cq, CallbackQuery):
        await message_or_cq.answer()
        m = message_or_cq.message
    else:
        m = message_or_cq

    await state.clear()
    await m.answer(
        "🎭 Мини-кастинг: короткий чек — пауза, тембр, ощущение. "
        "На выходе — 1 рекомендация и круг тренировки."
    )
    await m.answer(
        "Это мини-кастинг: 2–3 мин. Отвечай коротко. Готов?",
        reply_markup=kb_mc_start()
    )

# совместимость со старыми импортами
minicasting_entry = start_minicasting

# ── STEPS ────────────────────────────────────────────────────────────────────
@mc_router.callback_query(StateFilter("*"), F.data.in_({"mc:s0:yes", "mc:s0:no", "mc:s0:next"}))
async def mc_step1(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.update_data(s0=cq.data.split(":")[-1])
    await cq.message.answer("Q1. Удержал ли 2 сек тишины перед фразой?")
    await cq.message.answer("Выбери вариант:", reply_markup=kb_mc_q1())

@mc_router.callback_query(StateFilter("*"), F.data.startswith("mc:s1:"))
async def mc_step2(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.update_data(s1=cq.data.split(":")[-1])
    await cq.message.answer("Q2. Голос после паузы звучал ровнее?")
    await cq.message.answer("Выбери вариант:", reply_markup=kb_mc_q2())

@mc_router.callback_query(StateFilter("*"), F.data.startswith("mc:s2:"))
async def mc_step3(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.update_data(s2=cq.data.split(":")[-1])
    await cq.message.answer("Q3. Что было труднее?", reply_markup=kb_mc_q3())

@mc_router.callback_query(StateFilter("*"), F.data.startswith("mc:s3:"))
async def mc_summary(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    await state.update_data(s3=cq.data.split(":")[-1])

    data = await state.get_data()
    tip = "Точка роста: не давай паузе проваливаться." if data.get("s1") == "no" \
          else "Точка роста: удерживай тембр после паузы."

    await cq.message.answer(f"Итог: {tip}\nСделай 1 круг тренировки и вернись.")
    await cq.message.answer(
        "Оцени опыт 🔥/👌/😐 и добавь 1 слово-ощущение (необязательно).",
        reply_markup=kb_mc_rate()
    )

    # фиксация сессии (не критично, оборачиваем в try)
    try:
        answers = [data.get("s0"), data.get("s1"), data.get("s2"), data.get("s3")]
        result = "pause" if data.get("s1") == "no" else "ok"
        await save_casting_session(cq.from_user.id, answers=answers, result=result)
    except Exception:
        pass

@mc_router.callback_query(StateFilter("*"), F.data.startswith("mc:rate:"))
async def mc_rate(cq: CallbackQuery, state: FSMContext):
    await cq.answer()
    rate = cq.data.split(":")[-1]  # fire | ok | meh | skip

    if rate == "skip":
        await state.clear()
        await cq.message.answer("Спасибо! Возвращаю в меню.", reply_markup=main_menu_kb())
        return

    await state.update_data(rate=rate)
    await state.set_state(McState.wait_text)
    await cq.message.answer(
        "Принял эмодзи. Можешь одним словом дописать ощущение (до 140 симв) "
        "или напиши «/menu»."
    )

@mc_router.message(McState.wait_text)
async def mc_text_feedback(msg: Message, state: FSMContext):
    data = await state.get_data()
    phrase = (msg.text or "").strip()[:140]
    emoji = data.get("rate")  # fire|ok|meh

    try:
        await save_feedback(msg.from_user.id, emoji=emoji, phrase=phrase or None)
    except Exception:
        pass

    await state.clear()
    await msg.answer("Спасибо! Записал. Возвращаю в меню.", reply_markup=main_menu_kb())

__all__ = ["mc_router", "router", "start_minicasting", "minicasting_entry"]
