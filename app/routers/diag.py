# app/routers/diag.py
from __future__ import annotations

import platform
import hashlib
from datetime import datetime, timezone

import aiogram
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.build import BUILD_MARK
from app.config import settings

router = Router(name="diag")

_started_at = datetime.now(timezone.utc)


def _uptime_human() -> str:
    delta = datetime.now(timezone.utc) - _started_at
    total_sec = int(delta.total_seconds())
    h, m = divmod(total_sec // 60, 60)
    s = total_sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def _token_hash() -> str:
    return hashlib.md5(settings.bot_token.encode()).hexdigest()[:8]


async def _send_diag(target: Message | CallbackQuery):
    text = (
        "<b>Диагностика</b>\n"
        f"• BUILD: <code>{BUILD_MARK}</code>\n"
        f"• Python: <code>{platform.python_version()}</code>\n"
        f"• Aiogram: <code>{aiogram.__version__}</code>\n"
        f"• Uptime: <code>{_uptime_human()}</code>\n"
        f"• Token hash: <code>{_token_hash()}</code>\n"
    )
    if isinstance(target, CallbackQuery):
        await target.answer()
        await target.message.answer(text)
    else:
        await target.answer(text)


@router.message(F.text.in_({"/diag", "diag"}))
async def cmd_diag(msg: Message):
    await _send_diag(msg)


@router.callback_query(F.data == "go:diag")
async def go_diag(cb: CallbackQuery):
    await _send_diag(cb)
