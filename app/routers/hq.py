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
# from app.control.admin import AdminOnly  # если нужно ограничить — раскомментируй и см. низ файла

router = Router(name="hq")
log = logging.getLogger("hq")

RAW_HOST = "https://raw.githubusercontent.com"
REPO = os.getenv("GITHUB_REPOSITORY", "toinfo777-byte/elaya-stagecoach")
BRANCH = os.getenv("HQ_BRANCH", "main")
REPORT_DIR = os.getenv("HQ_REPORT_DIR", "docs/elaya_status")
STATUS_JSON_URL = os.getenv("STATUS_JSON_URL")  # напр. https://elaya-stagecoach-web.onrender.com/status_json


def _date_variants_utc(n: int = 3) -> list[str]:
    """Имена отчётов: сегодня/вчера/... (UTC)."""
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


@router.message(Command(commands=["hq"]))
async def cmd_hq(message: Message) -> None:
    log.info("HQ: handling /hq from chat %s", message.chat.id)

    # 1) ищем свежий отчёт (сегодня → вчера → позавчера)
    latest_name: Optional[str] = None
    async with aiohttp.ClientSession() as s:
        for cand in _date_variants_utc(3):
            if await _fetch_text(s, _report_url(cand)):
                latest_name = cand
                break
        # 2) стягиваем статус из веб-сервиса, если задан
        status = await _fetch_json(s, STATUS_JSON_URL) if STATUS_JSON_URL else None

    sha_full = (status or {}).get("sha") or os.getenv("GIT_SHA", "") or "unknown"
    sha7 = sha_full[:7] if isinstance(sha_full, str) and sha_full else "unknown"
    build = (status or {}).get("build") or os.getenv("BUILD_MARK", "unknown")
    env = (status or {}).get("env") or os.getenv("ENV", "develop")
    mode = (status or {}).get("mode") or os.getenv("MODE", "worker")
    uptime = (status or {}).get("uptime_sec")
    uptime_s = f"{uptime}s" if isinstance(uptime, int) else "n/a"

    lines = [
        "🧭 <b>HQ-сводка</b>",
        f"• ENV: <code>{env}</code>  • MODE: <code>{mode}</code>",
        f"• BUILD: <code>{build}</code>  • SHA: <code>{sha7}</code>",
        f"• Uptime: <code>{uptime_s}</code>",
    ]
    if latest_name:
        lines.append(f"• Отчёт: <code>{REPORT_DIR}/{latest_name}</code>")
        lines.append(f"• Raw: {_report_url(latest_name)}")
    else:
        lines.append("• Отчёт: не найден (проверьте daily/post-deploy отчёты)")

    await message.answer("\n".join(lines))

# Чтобы ограничить /hq только админам — раскомментируй:
# router.message.filter(AdminOnly())
