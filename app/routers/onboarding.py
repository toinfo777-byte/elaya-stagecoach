from __future__ import annotations

from datetime import datetime
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.state import StateFilter
from aiogram.types import Message

from app.texts.strings import (
    HELLO,
    CONSENT,
    ONBOARD_GOAL_PROMPT,
    ONBOARD_EXP_PROMPT,
    ONBOARD_TZ_PROMPT,
    ONBOARD_NAME_PROMPT,
)
from app.keyboards.menu import main_menu
from app.storage.repo import session_scope
from app.storage.models import User

router = Router(name="onboarding")


class Onboarding(StatesGroup):
    name = State()
    tz = State()
    goal = State()
    exp = State()
    consent = State()


def extract_start_payload(text: str | None) -> str | None:
    if not text:
        return None
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and parts[0].startswith("/start"):
        return parts[1].strip()
    return None


def _norm(s: str | None) -> str:
    return (s or "").strip().lower()


@router.message(StateFilter(None), CommandStart())
async def start(msg: Message, state: FSMContext):
    payload = extract_s_
