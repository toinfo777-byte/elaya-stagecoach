from __future__ import annotations

import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.storage.repo_extras import save_leader_intent, save_premium_request

# основной роутер модуля
leader_router = Router(name="leader")
# для обратной совместимости (если где-то импортируется router)
router = leader_router

# --- конфиг уведомлений админов (опционально) ---
ADMIN_ALERT_CHAT_ID = int(os.getenv("ADMIN_ALERT_CHAT_ID", "0") or 0)

# --- FSM ---
class LeaderStates(StatesGroup):
    micro = State()     # ждём одно слово-ощущение (до 140)
    premium = State()   # ждём 1 фразу цели (до 280)

# --- UI ---
def _intent_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Голос",                 callback_data="leader:intent:voice")],
        [InlineKeyboardButton(text="Публичные выступления", callback_data="leader:intent:public")],
        [InlineKeyboardButton(text="Сцена",                 callback_data="leader:intent:stage")],
        [InlineKeyboardButton(text="Другое",                callback_data="leader:intent:other")],
        [InlineKeyboardButton(text="🏠 В меню",             callback_data="go:menu")],
    ])

def _skip_or_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="leader:skip")],
        [InlineKeyboardButton(text="🏠 В меню",  callback_data="go:menu")],
    ])

# ---------- ПУБЛИЧНЫЙ ВХОД (его импортирует entrypoints.py) ----------
async def leader_entry(event: Message | CallbackQuery, state: FSMContext | None = None):
    """
    Единая точка входа: показывает экран выбора намерения.
    Работает и для Message, и для CallbackQuery.
    """
    text = "Путь лидера — твой вектор. 3 шага, 2–4 минуты.\nЧто важнее сейчас?"
    if isinstance(event, CallbackQuery):
        await event.answer()
        # состояние очищаем, если передано (entrypoints даёт state)
        if state is not None:
            await state.clear()
        await event.message.answer(text, reply_markup=_intent_kb())
    else:
        if state is not None:
            await state.clear()
        await event.answer(text, reply_markup=_intent_kb())

# ---------- ШАГ 1: выбор намерения ----------
@leader_router.callback_query(F.data.startswith("leader:intent:"))
async def _pick_intent(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    intent = cb.data.split(":")[-1]  # voice|public|stage|other
    await state.update_data(intent=intent)

    # первичная запись (intent без заметки)
    try:
        await save_leader_intent(cb.from_user.id, intent=intent, micro_note=None, upsert=False)
    except Exception:
        # на ошибке БД всё равно продолжаем сценарий
        pass

    # просим короткую микро-заметку
    await cb.message.answer(
        "Сделай 1 круг.\nОдним словом: что изменилось? (до 140 симв)",
        reply_markup=_skip_or_menu_kb()
    )
    await state.set_state(LeaderStates.micro)

# ---------- ШАГ 2: микро-заметка ----------
@leader_router.message(LeaderStates.micro, F.text)
async def _micro_note(msg: Message, state: FSMContext):
    note = (msg.text or "").strip()[:140]
    data = await state.get_data()
    intent = data.get("intent")

    # обновляем intent с микро-заметкой
    try:
        await save_leader_intent(msg.from_user.id, intent=intent, micro_note=note, upsert=True)
    except Exception:
        pass

    await msg.answer(
        "Оставь 1 фразу о цели. Это поможет подобрать формат. (до 280 симв)",
        reply_markup=_skip_or_menu_kb()
    )
    await state.set_state(LeaderStates.premium)

# ---------- ШАГ 3: фраза-цель / заявка ----------
@leader_router.message(LeaderStates.premium, F.text)
async def _premium_request(msg: Message, state: FSMContext):
    text = (msg.text or "").strip()[:280]
    data = await state.get_data()
    intent = data.get("intent")

    # сохраняем заявку
    try:
        await save_premium_request(user_id=msg.from_user.id, text=text, source="leader")
    except Exception:
        pass

    # уведомим админа (если настроено)
    if ADMIN_ALERT_CHAT_ID:
        u = msg.from_user
        alert = (f"⭐️ Premium request\n"
                 f"User: {u.full_name} (@{u.username}) id {u.id}\n"
                 f"Intent: {intent}\n"
                 f"Source: leader\n"
                 f"Text: {text}")
        try:
            await msg.bot.send_message(ADMIN_ALERT_CHAT_ID, alert)
        except Exception:
            pass

    await _finish_to_menu(msg, state)

# ---------- Пропуск на любом шаге (skip -> меню) ----------
@leader_router.callback_query(F.data == "leader:skip")
async def _skip_any(cb: CallbackQuery, state: FSMContext):
    await cb.answer("Ок")
    await _finish_to_menu(cb.message, state)

# ---------- Общий финиш ----------
async def _finish_to_menu(target: Message, state: FSMContext):
    await state.clear()
    await target.answer("✅ Заявка принята. Мы вернёмся с предложением.")

    # показать главное меню через общий хелпер
    try:
        from app.routers.help import show_main_menu
        await show_main_menu(target)
    except Exception:
        # на случай, если help ещё не подключён — мягко завершим
        await target.answer("Готово! Открываю меню.")


__all__ = ["leader_router", "router", "leader_entry", "LeaderStates"]
