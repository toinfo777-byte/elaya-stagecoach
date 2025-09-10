# app/routers/coach.py
from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta
from typing import Iterable

from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, MessageEntity
from aiogram.fsm.context import FSMContext

from app.config import settings
from app.keyboards.coach import timer_kb
from app.services.coach_rules import pick_drill_by_keywords
from app.storage.repo import session_scope, log_event
from app.storage.models import User

router = Router(name="coach")

# --- флаги и состояния ---
_COACH_USERS: dict[int, dict] = {}      # user_id -> {"until": dt, "last": monotonic_ts}
_ALLOWED_CHATS: set[int] = set()        # чаты, где включён групповой режим
_MAINTENANCE: bool = False              # быстрый выключатель
_GROUPS_DISABLED: bool = False          # глобально запретить групповой режим

_TTL_MIN_DEFAULT = 15
_RATE_SEC_DEFAULT = 5

# Тексты кнопок меню — игнорируем их в пассивном слушателе
_MENU_TEXTS: set[str] = {
    "🎯 Тренировка дня",
    "📈 Мой прогресс",
    "Путь лидера",
    "🎭 Мини-кастинг",
    "🔐 Политика",
    "💬 Помощь",
}

def _has_bot_command(entities: Iterable[MessageEntity] | None) -> bool:
    if not entities:
        return False
    return any(getattr(e, "type", None) == "bot_command" for e in entities)

def _coach_on(uid: int):
    ttl_min = getattr(settings, "coach_ttl_min", _TTL_MIN_DEFAULT)
    _COACH_USERS[uid] = {
        "until": datetime.utcnow() + timedelta(minutes=ttl_min),
        "last": 0.0,
    }

# ====== публичные команды / тексты ======
@router.message(StateFilter("*"), Command("coach_on"))
async def cmd_on(m: Message):
    if _MAINTENANCE:
        return await m.answer("🔧 Идут техработы. Попробуйте позже.")
    _coach_on(m.from_user.id)
    await m.answer("🤝 Личный режим наставника включён на 15 минут. "
                   "Сформулируйте коротко проблему — отвечу и предложу этюд.")

@router.message(StateFilter("*"), Command("coach_off"))
async def cmd_off(m: Message):
    _COACH_USERS.pop(m.from_user.id, None)
    await m.answer("👋 Личный режим наставника выключен.")

@router.message(StateFilter("*"), Command("coach_status"))
async def cmd_status(m: Message):
    uid = m.from_user.id
    st = _COACH_USERS.get(uid)
    personal = "включён до " + st["until"].strftime("%H:%M UTC") if st and datetime.utcnow() < st["until"] else "выключен"
    if m.chat.type in {"group", "supergroup"}:
        group = "включён" if m.chat.id in _ALLOWED_CHATS and not _GROUPS_DISABLED else "выключен"
        await m.answer(f"📊 Статус наставника:\n• Личный режим: {personal}\n• Групповой режим чата: {group}")
    else:
        await m.answer(f"📊 Статус наставника:\n• Личный режим: {personal}")

@router.message(StateFilter("*"), Command("ask"))
@router.message(StateFilter("*"), F.text.regexp(r"^/вопрос\s+.+"))
async def ask_cmd(m: Message):
    if _MAINTENANCE:
        return await m.answer("🔧 Идут техработы. Попробуйте позже.")
    text = m.text.split(maxsplit=1)[1] if " " in m.text else ""
    await _handle_question(m, text)

@router.message(
    StateFilter("*"),
    F.chat.type.in_({"group", "supergroup"}),
    Command("coach_toggle")
)
async def coach_toggle(m: Message):
    if _MAINTENANCE or _GROUPS_DISABLED:
        return await m.answer("🔕 Групповой режим сейчас недоступен.")
    cid = m.chat.id
    if cid in _ALLOWED_CHATS:
        _ALLOWED_CHATS.remove(cid)
        await m.answer("🔕 Групповой режим этого чата **выключён**.")
    else:
        _ALLOWED_CHATS.add(cid)
        await m.answer("🔔 Групповой режим этого чата **включён**.")

# ====== пассивное слушание ======
@router.message(F.text)
async def passive_listen(m: Message, state: FSMContext):
    if _MAINTENANCE:
        return  # тихо молчим во время техработ

    # Группы — только если включили, и глобально не отключено
    if m.chat.type in {"group", "supergroup"}:
        if _GROUPS_DISABLED or m.chat.id not in _ALLOWED_CHATS:
            return

    txt = (m.text or "").strip()
    if not txt or txt in _MENU_TEXTS:
        return
    if _has_bot_command(m.entities) or txt.startswith("/"):
        return

    uid = m.from_user.id
    st = _COACH_USERS.get(uid)
    if not st:
        return
    if datetime.utcnow() > st["until"]:
        _COACH_USERS.pop(uid, None)
        return await m.answer("⏳ Сессия наставника завершилась. Включить снова: /coach_on")

    # Rate limit
    rate_sec = getattr(settings, "coach_rate_sec", _RATE_SEC_DEFAULT)
    now = time.monotonic()
    if now - st["last"] < rate_sec:
        return
    st["last"] = now

    await _handle_question(m, txt)

# ====== служебные ======
async def _send_typing(bot, chat_id: int, stop_event: asyncio.Event):
    try:
        while not stop_event.is_set():
            await bot.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(5.5)
    except Exception:
        pass

async def _handle_question(m: Message, q: str):
    if not q.strip():
        return await m.answer("Сформулируй коротко, по сути. Например: «зажим в горле».")
    stop = asyncio.Event()
    typing_task = asyncio.create_task(_send_typing(m.bot, m.chat.id, stop))
    try:
        drill = pick_drill_by_keywords(q)
        title = drill["title"]
        steps = drill["steps"][:4]
        sign = drill.get("check_question", "Что изменится?")
        reply = (
            f"Коротко: попробуй это — {title}.\n"
            f"Шаги: " + " → ".join(steps) + ".\n"
            f"Признак: {sign}\n"
            f"Запусти таймер и отмечай ощущение одним словом."
        )
        # Логируем, но без падений
        try:
            with session_scope() as s:
                u = s.query(User).filter_by(tg_id=m.from_user.id).first()
                log_event(s, u.id if u else None, "coach_answer", {"q": q, "drill_id": drill.get("id")})
        except Exception:
            pass
        await m.answer(reply, reply_markup=timer_kb())
    except Exception:
        await m.answer("Ой, что-то пошло не так. Повтори шаг или вернись в меню: /menu 🙏")
        raise
    finally:
        stop.set()
        try:
            await typing_task
        except Exception:
            pass

@router.callback_query(F.data == "coach_timer_60")
async def coach_timer(cb: CallbackQuery):
    msg = await cb.message.answer("⏳ 60 сек.")
    for left in (45, 30, 15, 5):
        await asyncio.sleep(60 - left if left == 45 else 15 if left in (30, 15) else 10)
        await msg.edit_text(f"⏳ {left} сек.")
    await asyncio.sleep(5)
    await msg.edit_text("⏱ Готово! Как ощущение? Одно слово.")
    await cb.answer()

# ====== админ-команды быстрых флагов ======
def _is_admin(uid: int) -> bool:
    admin_ids = getattr(settings, "admin_ids", []) or []
    return uid in admin_ids

@router.message(StateFilter("*"), Command("maint_on"))
async def maint_on(m: Message):
    if not _is_admin(m.from_user.id):
        return
    global _MAINTENANCE
    _MAINTENANCE = True
    await m.answer("🔧 Режим техработ включён. Бот отвечает только на базовые команды.")

@router.message(StateFilter("*"), Command("maint_off"))
async def maint_off(m: Message):
    if not _is_admin(m.from_user.id):
        return
    global _MAINTENANCE
    _MAINTENANCE = False
    await m.answer("✅ Техработы выключены.")

@router.message(StateFilter("*"), Command("coach_groups_off"))
async def groups_off(m: Message):
    if not _is_admin(m.from_user.id):
        return
    global _GROUPS_DISABLED
    _GROUPS_DISABLED = True
    await m.answer("🔕 Глобально отключён групповой режим наставника.")

@router.message(StateFilter("*"), Command("coach_groups_on"))
async def groups_on(m: Message):
    if not _is_admin(m.from_user.id):
        return
    global _GROUPS_DISABLED
    _GROUPS_DISABLED = False
    await m.answer("🔔 Глобально включён групповой режим наставника.")
