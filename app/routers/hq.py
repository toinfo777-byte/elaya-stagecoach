from __future__ import annotations

import os
import time
from textwrap import dedent

from aiogram import Router, types, Bot
from aiogram.filters import Command

from app.core.alerts import send_admin_alert

router = Router()

_started_at = time.time()
_last_report_state: dict[str, str] = {}  # анти-дубликат по ключу env:build


def _uptime() -> str:
    sec = int(time.time() - _started_at)
    d, sec = divmod(sec, 86400)
    h, sec = divmod(sec, 3600)
    m, s = divmod(sec, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if s or not parts: parts.append(f"{s}s")
    return " ".join(parts)


def _env() -> str:
    return os.getenv("ENV") or os.getenv("ENVIRONMENT") or "unknown"


def _build() -> str:
    return os.getenv("BUILD_MARK") or os.getenv("RENDER_GIT_COMMIT") or "manual"


def _render_bits() -> str:
    bits = []
    for k in ("RENDER_SERVICE_NAME", "RENDER_INSTANCE_ID", "RENDER_REGION"):
        v = os.getenv(k)
        if v:
            key = k.replace("RENDER_", "").lower()
            bits.append(f"{key}=`{v}`")
    return " ".join(bits)


def build_hq_text(state: str = "Online") -> str:
    env = _env()
    build = _build()
    sha = os.getenv("RENDER_GIT_COMMIT") or ""
    render = _render_bits()

    lines = [
        f"🛰 Штабной отчёт — <b>{state}</b>",
        f"<code>env={env}</code> <code>build={build}</code>",
    ]
    if sha:
        lines.append(f"<code>sha={sha[:8]}</code>")
    if render:
        lines.append(render)
    lines.append(f"uptime=`{_uptime()}`")
    return dedent("\n".join(lines)).strip()


@router.message(Command("status"))
async def cmd_status(m: types.Message) -> None:
    await m.answer(build_hq_text("Online"))


@router.message(Command("panic"))
async def cmd_panic(m: types.Message, bot: Bot) -> None:
    """
    Безопасный тест аварийного оповещения.
    НИЧЕГО не роняем (никаких исключений), поэтому Telegram не ретраит,
    и спама не будет. Дедуп — на стороне send_admin_alert.
    """
    await m.answer("⚠️ Запускаю тест аварийного оповещения…")

    env = _env()
    build = _build()
    text = (
        "<b>Emergency alert</b>\n"
        f"env={env} build={build}\n"
        "Manual panic test"
    )
    await send_admin_alert(
        bot,
        text,
        dedup_key=f"panic:{env}:{build}",
    )
