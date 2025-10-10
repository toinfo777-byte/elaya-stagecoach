# app/routers/casting.py (шапка)
from __future__ import annotations

import re
import logging
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.keyboards.reply import main_menu_kb
from app.keyboards.inline import casting_skip_kb  # callback_data: "cast:skip_url"
from app.utils.admin import notify_admin

log = logging.getLogger(__name__)

# Надёжный импорт: сперва из repo, потом из repo_extras, затем локальный фолбэк
try:
    from app.storage.repo import save_casting  # наш основной вариант
except Exception:
    try:
        # если в образе ещё старая repo.py — используем заглушку из repo_extras
        from app.storage.repo_extras import save_casting_session as save_casting  # type: ignore
        log.warning("casting: using repo_extras.save_casting_session as save_casting fallback")
    except Exception:
        def save_casting(*, tg_id: int, name: str, age: int, city: str,
                         experience: str, contact: str, portfolio: str | None,
                         agree_contact: bool = True) -> None:
            log.warning(
                "casting: ultimate fallback; request not persisted | tg_id=%s name=%r age=%s city=%r exp=%r contact=%r portfolio=%r agree=%s",
                tg_id, name, age, city, experience, contact, portfolio, agree_contact
            )

router = Router(name="casting")
