from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.routers.help import show_main_menu
try:
    from app.storage.repo_extras import save_casting_session, save_feedback, log_progress_event
except Exception:
    async def save_casting_session(*args, **kwargs): return None
    async def save_feedback(*args, **kwargs): return None
    async def log_progress_event(*args, **kwargs): return None

mc_router = Router(name="minicasting")


class McState(StatesGroup):
    wait_word = State()


def _start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="mc:s0:yes"),
         InlineKeyboardButton(text="Нет", callback_data="mc:s0:no")],
        [InlineKeyboardButton(text="Дальше", callback_data="mc:s0:next")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])

def _rate_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥", callback_data="mc:rate:fire"),
         InlineKeyboardButton(text="👌", callback_data="mc:rate:ok"),
         InlineKeyboardButton(text="😐", callback_data="mc:rate:meh")],
        [InlineKeyboardButton(text="Пропустить", callback_data="mc:rate:skip")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])


async def start_minicasting(obj: Message | CallbackQuery, state: FSMContext | None = None):
    m = obj.message if isinstance(obj, CallbackQuery) else obj
    if isinstance(obj, CallbackQuery):
        await obj.answer()
    if state:
        await state.clear()
    await m.answer("🎭 Мини-кастинг: короткий чек 2–3 мин. Готов?", reply_markup=_start_kb())


@mc_router.callback_query(StateFilter("*"), F.data.startswith("mc:s0:"))
async def mc_begin(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer("Q1. Удержал ли 2 сек тишины перед фразой?")
    await cb.message.answer("Выбери: Да / Нет", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="mc:s1:yes"),
         InlineKeyboardButton(text="Нет", callback_data="mc:s1:no")],
        [InlineKeyboardButton(text="Дальше", callback_data="mc:s1:next"),
         InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ]))

@mc_router.callback_query(StateFilter("*"), F.data.startswith("mc:s1:"))
async def mc_q2(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer("Q2. Голос после паузы звучал ровнее?")
    await cb.message.answer("Выбери: Да / Нет", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="mc:s2:yes"),
         InlineKeyboardButton(text="Нет", callback_data="mc:s2:no")],
        [InlineKeyboardButton(text="Дальше", callback_data="mc:s2:next"),
         InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ]))

@mc_router.callback_query(StateFilter("*"), F.data.startswith("mc:s2:"))
async def mc_summary(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await cb.message.answer(
        "Итог: держи паузу и не роняй тембр.\n"
        "Оцени опыт и добавь 1 слово-ощущение (необязательно).",
        reply_markup=_rate_kb()
    )
    try:
        await save_casting_session(cb.from_user.id, answers=[], result="ok")
        await log_progress_event(cb.from_user.id, kind="minicasting", meta={})
    except Exception:
        pass

@mc_router.callback_query(StateFilter("*"), F.data.startswith("mc:rate:"))
async def mc_rate(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    rate = cb.data.split(":")[-1]  # fire|ok|meh|skip
    await state.update_data(emoji=None if rate == "skip" else rate)
    if rate == "skip":
        await cb.message.answer("Спасибо! Возвращаю в меню.")
        return await show_main_menu(cb)
    await state.set_state(McState.wait_word)
    await cb.message.answer("Принял эмодзи. Одним словом допиши ощущение (до 140 симв) или нажми «🏠 В меню».")

@mc_router.message(McState.wait_word)
async def mc_word(msg: Message, state: FSMContext):
    data = await state.get_data()
    phrase = (msg.text or "").strip()[:140]
    try:
        await save_feedback(msg.from_user.id, emoji=data.get("emoji", "ok"), phrase=phrase)
    except Exception:
        pass
    await state.clear()
    await msg.answer("Спасибо! Записал. Возвращаю в меню.")
    await show_main_menu(msg)
