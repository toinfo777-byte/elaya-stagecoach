# app/routers/hq.py
from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
# from app.control.admin import AdminOnly  # включи при необходимости

router = Router(name="hq")
log = logging.getLogger("hq")

RAW_HOST = "https://raw.githubusercontent.com"
REPO        = os.getenv("GITHUB_REPOSITORY", "toinfo777-byte/elaya-stagecoach")
BRANCH      = os.getenv("HQ_BRANCH", "main")
REPORT_DIR  = os.getenv("HQ_REPORT_DIR", "docs/elaya_status")

# URL твоего web-сервиса (из Render → Environment), например:
# https://elaya-stagecoach-web.onrender.com/status_json
STATUS_JSON_URL = os.getenv("STATUS_JSON_URL")

def _date_variants_utc(n: int = 3) -> list[str]:
    base = datetime.utcnow().date()
    return [f"Elaya_Status_{(base - timedelta(days=i)).isoformat().replace('-', '_')}.md" for i in range(n)]

async def _fetch_text(session: aiohttp.ClientSession, url: str, timeout: int = 10) -> Optional[str]:
    try:
        async with session.get(url, timeout=timeout) as r:
            if r.status == 200:
                return await r.text()
    except Exception:
        return None
    return None

async def _fetch_json(session: aiohttp.ClientSession, url: str, timeout: int = 8) -> Optional[dict]:
    try:
        async with session.get(url, timeout=timeout) as r:
            if r.status == 200:
                return await r.json()
    except Exception:
        return None
    return None

def _report_url(name: str) -> str:
    return f"{RAW_HOST}/{REPO}/{BRANCH}/{REPORT_DIR}/{name}"

def _sha7(val: Optional[str]) -> str:
    if isinstance(val, str) and val:
        return val[:7]
    return "unknown"

@router.message(Command(commands=["hq"]))
async def cmd_hq(message: Message) -> None:
    log.info("HQ: handling /hq from chat %s", message.chat.id)

    # ── 1) ищем свежий отчёт (сегодня → вчера → позавчера)
    latest_name: Optional[str] = None
    async with aiohttp.ClientSession() as s:
        for cand in _date_variants_utc(3):
            if await _fetch_text(s, _report_url(cand)):
                latest_name = cand
                break

        # ── 2) тянем статус web-сервиса (если задан URL)
        web_status = await _fetch_json(s, STATUS_JSON_URL) if STATUS_JSON_URL else None

    # ── Текущий бот-воркер (данные из ENV)
    bot_env   = os.getenv("ENV", "develop")
    bot_mode  = os.getenv("MODE", "worker")
    bot_build = os.getenv("BUILD_MARK", "unknown")
    # пробуем взять хэш сборки из разных мест
    bot_sha   = os.getenv("GIT_SHA") or os.getenv("SHORT_SHA") or "unknown"
    bot_sha7  = _sha7(bot_sha)

    # ── Web-сервис
    web_env   = (web_status or {}).get("env") or "n/a"
    web_mode  = (web_status or {}).get("mode") or "n/a"
    web_build = (web_status or {}).get("build") or "n/a"
    web_sha7  = _sha7((web_status or {}).get("sha"))
    web_up    = (web_status or {}).get("uptime_sec")
    web_up_s  = f"{web_up}s" if isinstance(web_up, int) else "n/a"

    # ── Карточка
    lines = [
        "🧭 <b>HQ-сводка</b>",
        f"• <u>Bot</u>: ENV=<code>{bot_env}</code> MODE=<code>{bot_mode}</code> BUILD=<code>{bot_build}</code> SHA=<code>{bot_sha7}</code>",
        f"• <u>Web</u>: ENV=<code>{web_env}</code> MODE=<code>{web_mode}</code> BUILD=<code>{web_build}</code> SHA=<code>{web_sha7}</code> Uptime=<code>{web_up_s}</code>",
    ]
    if latest_name:
        lines.append(f"• Отчёт: <code>{REPORT_DIR}/{latest_name}</code>")
        lines.append(f"• Raw: {_report_url(latest_name)}")
    else:
        lines.append("• Отчёт: не найден (проверьте daily/post-deploy отчёты)")

    await message.answer("\n".join(lines))

# Чтобы ограничить /hq только админам — раскомментируй:
# router.message.filter(AdminOnly())
