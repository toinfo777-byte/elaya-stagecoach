from __future__ import annotations
import asyncio, time
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext

from app.config import settings
from app.keyboards.coach import timer_kb
from app.services.coach_rules import pick_drill_by_keywords
from app.storage.repo import session_scope, log_event
from app.storage.models import User

router = Router(name="coach")

_COACH_USERS: dict[int, dict] = {}   # user_id -> {"until": dt, "last": ts}
_ALLOWED_CHATS: set[int] = set()     # включено через /coach_toggle

def _coach_on(u: int):
    _COACH_USERS[u] = {"until": datetime.utcnow() + timedelta(minutes=settings.coach_ttl_min), "last": 0.0}

async def coach_on(m: Message):
    _coach_on(m.from_user.id)
    await m.answer("🤝 Наставник включён на 15 минут. Спроси коротко — отвечу и предложу этюд.")

@router.message(Command("coach_on"))
async def cmd_on(m: Message):
    await coach_on(m)

@router.message(Command("coach_off"))
async def cmd_off(m: Message):
    _COACH_USERS.pop(m.from_user.id, None)
    await m.answer("👋 Наставник выключен.")

@router.message(Command("ask"))
@router.message(F.text.regexp(r"^/вопрос\s+.+"))
async def ask_cmd(m: Message):
    text = m.text.split(maxsplit=1)[1] if " " in m.text else ""
    await _handle_question(m, text)

@router.message(F.chat.type.in_({"group","supergroup"}), Command("coach_toggle"))
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
    # групповые обсуждения — только если включили
    if m.chat.type in {"group","supergroup"} and m.chat.id not in _ALLOWED_CHATS:
        return
    # работать только когда включен и в рамках TTL
    u = m.from_user.id
    st = _COACH_USERS.get(u)
    if not st:
        return
    if datetime.utcnow() > st["until"]:
        _COACH_USERS.pop(u, None)
        return await m.answer("⏳ Сессия наставника завершилась. Включить снова: /coach_on")

    # rate limit
    now = time.monotonic()
    if now - st["last"] < settings.coach_rate_sec:
        return  # молча
    st["last"] = now
    await _handle_question(m, m.text)

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

    # typing…
    stop = asyncio.Event()
    asyncio.create_task(_send_typing(m.bot, m.chat.id, stop))

    # подбираем этюд (fallback без LLM)
    drill = pick_drill_by_keywords(q)
    title = drill["title"]
    steps = drill["steps"][:4]
    sign  = drill.get("check_question","Что изменится?")

    reply = (
        f"Коротко: попробуй это — {title}.\n"
        f"Шаги: " + " → ".join(steps) + ".\n"
        f"Признак: {sign}\n"
        f"Запусти таймер и отмечай ощущение одним словом."
    )
    # лог
    with session_scope() as s:
        u = s.query(User).filter_by(tg_id=m.from_user.id).first()
        log_event(s, u.id if u else None, "coach_answer", {"q": q, "drill_id": drill["id"]})

    stop.set()
    await m.answer(reply, reply_markup=timer_kb())

@router.callback_query(F.data == "coach_timer_60")
async def coach_timer(cb: CallbackQuery):
    msg = await cb.message.answer("⏳ 60 сек.")
    for left in (45, 30, 15, 5):
        await asyncio.sleep(60 - left if left == 45 else 15 if left in (30,15) else 10)
        await msg.edit_text(f"⏳ {left} сек.")
    await asyncio.sleep(5)
    await msg.edit_text("⏱ Готово! Как ощущение? Одно слово.")
    await cb.answer()
