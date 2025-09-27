from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.routers.help import show_main_menu
try:
    from app.storage.repo_extras import save_leader_intent, save_premium_request, log_progress_event
except Exception:
    async def save_leader_intent(*args, **kwargs): return None
    async def save_premium_request(*args, **kwargs): return None
    async def log_progress_event(*args, **kwargs): return None

leader_router = Router(name="leader")


class LeaderState(StatesGroup):
    note = State()


def _intent_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Голос", callback_data="lp:intent:voice")],
        [InlineKeyboardButton(text="Публичные выступления", callback_data="lp:intent:public")],
        [InlineKeyboardButton(text="Сцена", callback_data="lp:intent:stage")],
        [InlineKeyboardButton(text="Другое", callback_data="lp:intent:other")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")],
    ])


async def leader_entry(obj: Message | CallbackQuery):
    text = "Путь лидера — твой вектор. 3 шага, 2–4 минуты.\nЧто важнее сейчас?"
    if isinstance(obj, CallbackQuery):
        await obj.answer()
        await obj.message.answer(text, reply_markup=_intent_kb())
    else:
        await obj.answer(text, reply_markup=_intent_kb())


@leader_router.callback_query(StateFilter("*"), F.data.startswith("lp:intent:"))
async def lp_pick(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    intent = cb.data.split(":")[-1]
    await state.update_data(intent=intent)
    try:
        await save_leader_intent(cb.from_user.id, intent=intent, micro_note=None, upsert=False)
        await log_progress_event(cb.from_user.id, kind="leader_path", meta={"intent": intent})
    except Exception:
        pass
    await cb.message.answer(
        "Сделай 1 круг. Одним словом: что изменилось? (до 140 симв)\n"
        "Потом вернусь с предложением ⭐️",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В меню", callback_data="go:menu")]
        ])
    )
    await state.set_state(LeaderState.note)

@leader_router.message(LeaderState.note)
async def lp_note(msg: Message, state: FSMContext):
    note = (msg.text or "").strip()[:140]
    data = await state.get_data()
    try:
        await save_leader_intent(msg.from_user.id, intent=data.get("intent", "other"), micro_note=note, upsert=True)
        await save_premium_request(user_id=msg.from_user.id, text=note, source="leader")
    except Exception:
        pass
    await state.clear()
    await msg.answer("✅ Заявка принята. Мы вернёмся с предложением.")
    await show_main_menu(msg)
