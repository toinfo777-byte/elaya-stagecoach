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

# user_id -> {"until": dt, "last": monotonic_ts}
_COACH_USERS: dict[int, dict] = {}
# Разрешённые групповые чаты для /coach_toggle
_ALLOWED_CHATS: set[int] = set()

_TTL_MIN_DEFAULT = 15
_RATE_SEC_DEFAULT = 5

# Тексты из меню — их наставник должен игнорировать
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
    # aiogram v3: entity.type == "bot_command"
    return any(getattr(e, "type", None) == "bot_command" for e in entities)

def _coach_on(uid: int):
    ttl_min = getattr(settings, "coach_ttl_min", _TTL_MIN_DEFAULT)
    _COACH_USERS[uid] = {
        "until": datetime.utcnow() + timedelta(minutes=ttl_min),
        "last": 0.0,
    }

async def coach_on(m: Message):
    _coach_on(m.from_user.id)
    await m.answer("🤝 Наставник включён на 15 минут. Спроси коротко — отвечу и предложу этюд.")

@router.message(StateFilter("*"), Command("coach_on"))
async def cmd_on(m: Message):
    await coach_on(m)

@router.message(StateFilter("*"), Command("coach_off"))
async def cmd_off(m: Message):
    _COACH_USERS.pop(m.from_user.id, None)
    await m.answer("👋 Наставник выключен.")

@router.message(StateFilter("*"), Command("ask"))
@router.message(StateFilter("*"), F.text.regexp(r"^/вопрос\s+.+"))
async def ask_cmd(m: Message):
    text = m.text.split(maxsplit=1)[1] if " " in m.text else ""
    await _handle_question(m, text)

@router.message(
    StateFilter("*"),
    F.chat.type.in_({"group", "supergroup"}),
    Command("coach_toggle")
)
async def coach_toggle(m: Message):
    cid = m.chat.id
    if cid in _ALLOWED_CHATS:
        _ALLOWED_CHATS.remove(cid)
        await m.answer("🔕 В этом чате наставник отключён.")
    else:
        _ALLOWED_CHATS.add(cid)
        await m.answer("🔔 В этом чате наставник включён.")

@router.message(F.text)
async def passive_listen(m: Message, state: FSMContext):
    """
    Молчим на:
      - бот-команды (/start, /menu, /help и пр.)
      - тексты кнопок меню
      - пустые/пробельные сообщения
    Слушаем только когда включён наставник и не истёк TTL.
    """
    # Группы — только если включили
    if m.chat.type in {"group", "supergroup"} and m.chat.id not in _ALLOWED_CHATS:
        return

    txt = (m.text or "").strip()
    if not txt:
        return
    if txt in _MENU_TEXTS:
        return
    if _has_bot_command(m.entities):
        return
    if txt.startswith("/"):  # подстрахуемся
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
        await m.answer("Ой, что-то пошло не так. Попробуй ещё раз одной короткой фразой 🙏")
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
