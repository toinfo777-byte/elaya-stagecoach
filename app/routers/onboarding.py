# app/routers/onboarding.py
from __future__ import annotations

import re
import importlib
import inspect
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters.command import CommandObject

from app.keyboards.menu import main_menu
from app.texts.strings import (
    HELLO, CONSENT,
    ONBOARD_GOAL_PROMPT, ONBOARD_EXP_PROMPT,
    ONBOARD_TZ_PROMPT, ONBOARD_NAME_PROMPT,
)
from app.storage.repo import session_scope
from app.storage.models import User

router = Router(name="onboarding")

class Onboarding(StatesGroup):
    name = State()
    tz = State()
    goal = State()
    exp = State()
    consent = State()

TRAINING_RE = re.compile(r"^go_training(?:_post_(?P<id>\d+))?$")
CASTING_RE  = re.compile(r"^go_casting(?:_post_(?P<id>\d+))?$")
APPLY_RE    = re.compile(r"^go_apply(?:_post_(?P<id>\d+))?$")

def _norm(s: str | None) -> str:
    return (s or "").strip()

def _is_yes_consent(text: str | None) -> bool:
    return _norm(text).lower().startswith("соглас")

def _get_user_by_tg(user_id: int) -> User | None:
    with session_scope() as s:
        return s.query(User).filter(User.tg_id == user_id).one_or_none()

def _save_or_update_user_by_tg(user_id: int, data: dict):
    with session_scope() as s:
        u = s.query(User).filter(User.tg_id == user_id).one_or_none()
        if not u:
            u = User(tg_id=user_id)
            s.add(u)
        u.name = data.get("name") or u.name
        u.tz = data.get("tz") or u.tz
        u.goal = data.get("goal") or u.goal
        if data.get("exp") is not None:
            try:
                u.exp_level = int(str(data["exp"]).strip())
            except Exception:
                pass
        if data.get("start_payload"):
            u.source = data["start_payload"]
        u.last_seen = datetime.utcnow()
        s.flush()

async def _try_call(module_name: str, candidates: list[str], msg: Message, **kwargs):
    """
    Пытаемся импортировать модуль и вызвать первую найденную корутину
    из списка candidates. Лишние kwargs отбрасываем.
    """
    mod = importlib.import_module(module_name)
    for name in candidates:
        fn = getattr(mod, name, None)
        if fn and inspect.iscoroutinefunction(fn):
            # берем только поддерживаемые параметры
            sig = inspect.signature(fn)
            call_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
            return await fn(
