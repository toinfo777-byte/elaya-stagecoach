# app/routers/hq.py
from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

# из своего проекта: опционально можно включить фильтр админов
# from app.control.admin import AdminOnly

router = Router(name="hq")

RAW_HOST = "https://raw.githubusercontent.com"
REPO = os.getenv("GITHUB_REPOSITORY", "toinfo777-byte/elaya-stagecoach")
BRANCH = os.getenv("HQ_BRANCH", "main")
REPORT_DIR = os.getenv("HQ_REPORT_DIR", "docs/elaya_status")
STATUS_JSON_URL = os.getenv("STATUS_JSON_URL")  # напр. https://elaya-stagecoach-web.onrender.com/status_json


def _date_variants_utc(n: int = 2) -> list[str]:
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


@router.message(Command("hq"))
async def cmd_hq(message: Message) -> None:
    """Короткая HQ-сводка: build/sha/uptime + ссылка на последний отчёт."""
    latest_name: Optional[str] = None
    async with aiohttp.ClientSession() as s:
        for cand in _date_variants_utc(3):
            url = _report_url(cand)
            txt = await _fetch_text(s, url)
            if txt:
                latest_name = cand
                break

        status = await _fetch_json(s, STATUS_JSON_URL) if STATUS_JSON_URL else None

    sha = (status or {}).get("sha") or "unknown"
    sha7 = sha[:7] if isinstance(sha, str) else "unknown"
    build = (status or {}).get("build") or os.getenv("BUILD_MARK", "unknown")
    env = (status or {}).get("env") or os.getenv("ENV", "develop")
    mode = (status or {}).get("mode") or ("web" if STATUS_JSON_URL else "worker")
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

# Чтобы ограничить команду только для админов — раскомментируй:
# router.message.filter(AdminOnly())
