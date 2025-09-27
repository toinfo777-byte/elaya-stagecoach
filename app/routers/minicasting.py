# app/routers/minicasting.py
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)

mc_router = Router(name="minicasting")  # <-- main.py импортирует mc_router

# ---------- UI ----------
def _kb_start() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да",     callback_data="mc:s0:yes"),
         InlineKeyboardButton(text="Нет",    callback_data="mc:s0:no")],
        [InlineKeyboardButton(text="Дальше", callback_data="mc:s0:next")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def _kb_q1() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да",  callback_data="mc:s1:yes"),
         InlineKeyboardButton(text="Нет", callback_data="mc:s1:no")],
        [InlineKeyboardButton(text="Дальше", callback_data="mc:s1:next"),
         InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def _kb_q2() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да",  callback_data="mc:s2:yes"),
         InlineKeyboardButton(text="Нет", callback_data="mc:s2:no")],
        [InlineKeyboardButton(text="Дальше", callback_data="mc:s2:next"),
         InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def _kb_q3() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пауза",  callback_data="mc:s3:pause"),
         InlineKeyboardButton(text="Тембр",  callback_data="mc:s3:timbre"),
         InlineKeyboardButton(text="То же",  callback_data="mc:s3:same")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def _kb_rate() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥", callback_data="mc:rate:fire"),
         InlineKeyboardButton(text="👌", callback_data="mc:rate:ok"),
         InlineKeyboardButton(text="😐", callback_data="mc:rate:meh")],
        [InlineKeyboardButton(text="Пропустить", callback_data="mc:rate:skip")],
    ])

class McState(StatesGroup):
    wait_text = State()

# ---------- entry ----------
async def start_minicasting(obj: Message | CallbackQuery, state: FSMContext | None = None):
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        m = obj.message
    else:
        m = obj
    if state:
        await state.clear()
    await m.answer("🎭 Мини-кастинг: короткий чек 2–3 мин. Готов?",
                   reply_markup=_kb_start())

@mc_router.message(Command("casting"))
async def cmd_casting(m: Message, state: FSMContext):
    await start_minicasting(m, state)

# ---------- steps ----------
@mc_router.callback_query(StateFilter("*"), F.data.in_({"mc:s0:yes", "mc:s0:no", "mc:s0:next"}))
async def mc_step1(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(s0=cb.data.split(":")[-1])
    await cb.message.answer("Q1. Удержал ли 2 сек тишины перед фразой?",
                            reply_markup=_kb_q1())

@mc_router.callback_query(StateFilter("*"), F.data.startswith("mc:s1:"))
async def mc_step2(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(s1=cb.data.split(":")[-1])
    await cb.message.answer("Q2. Голос после паузы звучал ровнее?",
                            reply_markup=_kb_q2())

@mc_router.callback_query(StateFilter("*"), F.data.startswith("mc:s2:"))
async def mc_step3(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(s2=cb.data.split(":")[-1])
    await cb.message.answer("Q3. Что было труднее?", reply_markup=_kb_q3())

@mc_router.callback_query(StateFilter("*"), F.data.startswith("mc:s3:"))
async def mc_summary(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.update_data(s3=cb.data.split(":")[-1])
    data = await state.get_data()
    tip = "Точка роста: не давай паузе проваливаться." if data.get("s1") == "no" \
        else "Точка роста: удерживай тембр после паузы."
    await cb.message.answer(f"Итог: {tip}\nСделай 1 круг тренировки и вернись.")
    await cb.message.answer("Оцени опыт 🔥/👌/😐 и добавь 1 слово-ощущение (необязательно).",
                            reply_markup=_kb_rate())

@mc_router.callback_query(StateFilter("*"), F.data.startswith("mc:rate:"))
async def mc_rate(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    rate = cb.data.split(":")[-1]
    await state.update_data(rate=rate)
    if rate == "skip":
        await state.clear()
        from app.routers.help import show_main_menu
        await cb.message.answer("Спасибо! Возвращаю в меню.")
        return await show_main_menu(cb)
    await state.set_state(McState.wait_text)
    await cb.message.answer("Принял эмодзи. Можешь одним словом дописать ощущение (до 140 симв) "
                            "или нажми «/menu».")

@mc_router.message(McState.wait_text, F.text.len() > 0)
async def mc_text_feedback(m: Message, state: FSMContext):
    txt = (m.text or "").strip()[:140]
    try:
        from app.storage.repo_extras import save_feedback, log_progress_event
        data = await state.get_data()
        await save_feedback(user_id=m.from_user.id, emoji=data.get("rate"), phrase=txt)
        await log_progress_event(m.from_user.id, kind="minicasting", meta=None)
    except Exception:
        pass
    await state.clear()
    from app.routers.help import show_main_menu
    await m.answer("Спасибо! Записал. Возвращаю в меню.")
    await show_main_menu(m)
