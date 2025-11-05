from __future__ import annotations

import time
from textwrap import dedent

import aiohttp

from app.config import settings

_started = time.time()


def uptime_human() -> str:
    sec = int(time.time() - _started)
    d, sec = divmod(sec, 86400)
    h, sec = divmod(sec, 3600)
    m, s = divmod(sec, 60)
    parts: list[str] = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if s or not parts:
        parts.append(f"{s}s")
    return " ".join(parts)


def build_hq_message() -> str:
    lines: list[str] = [
        "🛰 <b>HQ-сводка</b>",
        f"• <b>Bot</b>: ENV=`{settings.env}` MODE=`{settings.mode}` BUILD=`{settings.build_mark}`",
    ]

    sha = settings.render_git_commit
    if sha:
        lines.append(f"• SHA: `{sha[:8]}`")

    render_bits: list[str] = []
    if settings.render_service:
        render_bits.append(f"svc=`{settings.render_service}`")
    if settings.render_instance:
        render_bits.append(f"inst=`{settings.render_instance}`")
    if settings.render_region:
        render_bits.append(f"region=`{settings.render_region}`")
    if render_bits:
        lines.append("• Render: " + " ".join(render_bits))

    lines.append(f"• Uptime: `{uptime_human()}`")
    lines.append("• Отчёт: не найден (проверьте daily/post-deploy отчёты)")
    return dedent("\n".join(lines))


async def get_render_status() -> str:
    """
    Возвращает краткий отчёт о последнем деплое Render.
    Требует: settings.render_api_key, settings.render_service_id
    """
    if not settings.render_api_key or not settings.render_service_id:
        return "ℹ️ Render API не настроен."

    url = f"https://api.render.com/v1/services/{settings.render_service_id}/deploys"
    headers = {"Authorization": f"Bearer {settings.render_api_key}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=15) as resp:
                if resp.status != 200:
                    return f"⚠️ Render API error: {resp.status}"
                data = await resp.json()
    except Exception as e:
        return f"⚠️ Ошибка при запросе Render API: {e}"

    if not data:
        return "ℹ️ Нет данных о деплоях Render."

    latest = data[0] or {}
    commit = (latest.get("commit") or "")[:8] or "—"
    branch = latest.get("branch", "—")
    status = latest.get("status", "—")
    created = latest.get("createdAt", "—")
    updated = latest.get("updatedAt", "—")

    msg = dedent(
        f"""
        🧱 <b>Render Build</b>
        • Branch: `{branch}`
        • Commit: `{commit}`
        • Status: `{status}`
        • Created: `{created}`
        • Updated: `{updated}`
        """
    ).strip()
    return msg
