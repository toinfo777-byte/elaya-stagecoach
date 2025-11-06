from __future__ import annotations

import os
import time
from textwrap import dedent

from aiogram import Router, types, Bot
from aiogram.filters import Command

# NEW: централизованная отправка с дедупликацией
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


async def send_hq_report(bot: Bot, chat_id: int, state: str) -> None:
    """Публикуем отчёт только если состояние изменилось."""
    key = f"{_env()}:{_build()}"
    prev = _last_report_state.get(key)
    if prev == state:
        return
    _last_report_state[key] = state
    await bot.send_message(chat_id, build_hq_text(state))


@router.message(Command("status"))
async def cmd_status(m: types.Message) -> None:
    await m.answer(build_hq_text("Online"))


@router.message(Command("panic"))
async def cmd_panic(m: types.Message) -> None:
    """
    Тест аварийки: шлём админ-алерт с дедупликацией.
    Процесс НЕ падает (чтобы не плодить триггеры и дубли).
    Если хочется уметь «уронить» по флагу — см. PANIC_RAISE ниже.
    """
    await m.answer("⚠️ Запускаю тест аварийного оповещения…")

    text = (
        "<b>⚠️ Emergency alert</b>\n"
        f"env={_env()} build={_build()}\n"
        "Manual panic test"
    )
    # ключ учитывает окружение/сборку, чтобы не летели дубликаты
    await send_admin_alert(m.bot, text, dedup_key=f"panic:{_env()}:{_build()}")

    # Опционально: разрешить «падение» через env-флаг
    if (os.getenv("PANIC_RAISE") or "").lower() in {"1", "true", "yes"}:
        raise RuntimeError("Manual panic test (forced by PANIC_RAISE)")
