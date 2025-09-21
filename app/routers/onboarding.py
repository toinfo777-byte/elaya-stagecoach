from __future__ import annotations
import re
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

# go_training[_post_<id>] / go_casting[_post_<id>] / go_apply[_post_<id>]
TRAINING_RE = re.compile(r"^go_training(?:_post_(?P<id>\d+))?$")
CASTING_RE  = re.compile(r"^go_casting(?:_post_(?P<id>\d+))?$")
APPLY_RE    = re.compile(r"^go_casting(?:_post_(?P<id>\d+))?$".replace("casting", "apply"))

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

async def _route_by_payload(msg: Message, payload: str):
    p = (payload or "").strip()

    m = TRAINING_RE.match(p)
    if m:
        from app.routers.training import open_training
        await open_training(msg, source=p, post_id=m.group("id"))
        return

    m = CASTING_RE.match(p)
    if m:
        from app.routers.casting import open_casting
        await open_casting(msg, source=p, post_id=m.group("id"))
        return

    m = APPLY_RE.match(p)
    if m:
        from app.routers.apply import open_apply
        await open_apply(msg, source=p, post_id=m.group("id"))
        return

    # эвристика по префиксу — на всякий
    if p.startswith("go_casting"):
        from app.routers.casting import open_casting
        await open_casting(msg, source=p, post_id=None)
        return
    if p.startswith("go_training"):
        from app.routers.training import open_training
        await open_training(msg, source=p, post_id=None)
        return
    if p.startswith("go_apply"):
        from app.routers.apply import open_apply
        await open_apply(msg, source=p, post_id=None)
        return

    await msg.answer("Готово. Вот меню:", reply_markup=main_menu())

# -------- старт / онбординг --------

# 1) Старт без состояния
@router.message(StateFilter(None), CommandStart(deep_link=True))
async def start_with_deeplink(msg: Message, state: FSMContext, command: CommandObject):
    payload = (command.args or "").strip() if command else ""
    existing = _get_user_by_tg(msg.from_user.id)

    if existing:
        if payload:
            await _route_by_payload(msg, payload)
            return
        await msg.answer("Готово. Вот меню.", reply_markup=main_menu())
        return

    if payload:
        await state.update_data(start_payload=payload)

    await msg.answer(HELLO)
    await msg.answer(ONBOARD_NAME_PROMPT)
    await state.set_state(Onboarding.name)

@router.message(StateFilter(None), CommandStart())
async def start_plain(msg: Message, state: FSMContext):
    existing = _get_user_by_tg(msg.from_user.id)
    if existing:
        await msg.answer("Готово. Вот меню.", reply_markup=main_menu())
        return
    await msg.answer(HELLO)
    await msg.answer(ONBOARD_NAME_PROMPT)
    await state.set_state(Onboarding.name)

# 2) Старт из ЛЮБОГО состояния — очищаем стейт и запускаем заново (сохраняем payload)
@router.message(~StateFilter(None), CommandStart(deep_link=True))
async def restart_with_deeplink(msg: Message, state: FSMContext, command: CommandObject):
    await state.clear()
    await start_with_deeplink(msg, state, command)

@router.message(~StateFilter(None), CommandStart())
async def restart_plain(msg: Message, state: FSMContext):
    await state.clear()
    await start_plain(msg, state)

# Управление состоянием
@router.message(~StateFilter(None), Command("cancel"))
async def cancel_anywhere(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Анкета сброшена. Возвращаю в меню.", reply_markup=main_menu())

@router.message(~StateFilter(None), Command("menu"))
async def menu_anywhere(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Готово. Вот меню:", reply_markup=main_menu())

# Во время анкеты блокируем только слэш-команды — reply-кнопки/эмодзи проходят
@router.message(~StateFilter(None), F.text.startswith("/"))
async def in_form_but_command(msg: Message):
    await msg.answer("Вы сейчас заполняете короткую анкету. Напишите ответ или /cancel, чтобы выйти.")

# -------- шаги анкеты --------
@router.message(Onboarding.name, F.text.len() > 0)
async def set_name(msg: Message, state: FSMContext):
    await state.update_data(name=_norm(msg.text))
    await msg.answer(ONBOARD_TZ_PROMPT)
    await state.set_state(Onboarding.tz)

@router.message(Onboarding.tz, F.text.len() > 0)
async def set_tz(msg: Message, state: FSMContext):
    await state.update_data(tz=_norm(msg.text))
    await msg.answer(ONBOARD_GOAL_PROMPT)
    await state.set_state(Onboarding.goal)

@router.message(Onboarding.goal, F.text.len() > 0)
async def set_goal(msg: Message, state: FSMContext):
    await state.update_data(goal=_norm(msg.text))
    await msg.answer(ONBOARD_EXP_PROMPT)
    await state.set_state(Onboarding.exp)

@router.message(Onboarding.exp, F.text.len() > 0)
async def set_exp(msg: Message, state: FSMContext):
    await state.update_data(exp=_norm(msg.text))
    await msg.answer(CONSENT)
    await state.set_state(Onboarding.consent)

@router.message(Onboarding.consent, F.text.func(_is_yes_consent))
async def finalize(msg: Message, state: FSMContext):
    data = await state.get_data()
    _save_or_update_user_by_tg(msg.from_user.id, data)
    await state.clear()
    await msg.answer("Готово! Открываю меню.", reply_markup=main_menu())

    if data.get("start_payload"):
        await _route_by_payload(msg, data["start_payload"])

@router.message(Onboarding.consent)
async def ask_consent_again(msg: Message):
    await msg.answer("Пожалуйста, напишите «Согласен» (или /cancel, чтобы выйти).")
