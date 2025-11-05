from __future__ import annotations

import time
from textwrap import dedent
from typing import Any, Dict, List

import aiohttp

from app.config import settings

# ─────────────────────────────────────────────────────────────────────────────
# Uptime helpers
# ─────────────────────────────────────────────────────────────────────────────
_started = time.time()


def uptime_human() -> str:
    sec = int(time.time() - _started)
    d, sec = divmod(sec, 86400)
    h, sec = divmod(sec, 3600)
    m, s = divmod(sec, 60)
    parts: List[str] = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if s or not parts:
        parts.append(f"{s}s")
    return " ".join(parts)


def _short_sha(sha: str | None, ln: int = 8) -> str:
    if not sha:
        return "—"
    sha = sha.strip()
    return sha[:ln] if len(sha) >= ln else sha


# ─────────────────────────────────────────────────────────────────────────────
# HQ message (HTML, т.к. bot настроен на ParseMode.HTML)
# ─────────────────────────────────────────────────────────────────────────────
def build_hq_message() -> str:
    """
    Возвращает короткую HQ-сводку в HTML: env/mode/build, render-маркеры и аптайм.
    """
    lines: List[str] = [
        "🛰 <b>HQ-сводка</b>",
        f"• <b>Bot</b>: ENV=<code>{settings.env}</code> "
        f"MODE=<code>{settings.mode}</code> "
        f"BUILD=<code>{settings.build_mark}</code>",
    ]

    sha = _short_sha(getattr(settings, "render_git_commit", None))
    if sha and sha != "—":
        lines.append(f"• <b>SHA</b>: <code>{sha}</code>")

    render_bits: List[str] = []
    svc = getattr(settings, "render_service", None)
    inst = getattr(settings, "render_instance", None)
    region = getattr(settings, "render_region", None)

    if svc:
        render_bits.append(f"svc=<code>{svc}</code>")
    if inst:
        render_bits.append(f"inst=<code>{inst}</code>")
    if region:
        render_bits.append(f"region=<code>{region}</code>")

    if render_bits:
        lines.append("• <b>Render</b>: " + " ".join(render_bits))

    lines.append(f"• <b>Uptime</b>: <code>{uptime_human()}</code>")
    lines.append("• <b>Отчёт</b>: не найден (см. nightly/ post-deploy отчёты)")

    # Итог — HTML
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Render API helpers
# ─────────────────────────────────────────────────────────────────────────────
async def get_render_status() -> str:
    """
    Возвращает краткий отчёт о последнем деплое Render в HTML.
    Требуются: RENDER_API_KEY и RENDER_SERVICE_ID.
    """
    api_key = getattr(settings, "render_api_key", None)
    service_id = getattr(settings, "render_service_id", None)

    if not api_key or not service_id:
        return (
            "⚠️ <b>Render</b>: не настроены <code>RENDER_API_KEY</code> "
            "и/или <code>RENDER_SERVICE_ID</code>."
        )

    url = f"https://api.render.com/v1/services/{service_id}/deploys"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return f"⚠️ <b>Render API</b>: HTTP <code>{resp.status}</code>"
                data: List[Dict[str, Any]] = await resp.json()  # type: ignore[assignment]
    except Exception as e:
        return f"⚠️ <b>Render API</b>: ошибка запроса — <code>{e}</code>"

    if not data:
        return "ℹ️ <b>Render</b>: данных о деплоях нет."

    latest = data[0] or {}
    commit = _short_sha(latest.get("commit"))
    branch = latest.get("branch") or "—"
    status = latest.get("status") or "—"
    created = latest.get("createdAt") or "—"
    updated = latest.get("updatedAt") or "—"

    # Немного косметики статуса
    status_badge = {
        "live": "✅ live",
        "succeeded": "✅ succeeded",
        "failed": "❌ failed",
        "build_failed": "❌ build_failed",
        "canceled": "⏹ canceled",
        "deactivated": "⏸ deactivated",
        "in_progress": "⏳ in_progress",
        "queued": "⏳ queued",
    }.get(str(status).lower(), str(status))

    msg = dedent(
        f"""
        🧱 <b>Render Build</b>
        • Branch: <code>{branch}</code>
        • Commit: <code>{commit}</code>
        • Status: <code>{status_badge}</code>
        • Created: <code>{created}</code>
        • Updated: <code>{updated}</code>
        """
    ).strip()

    return msg
