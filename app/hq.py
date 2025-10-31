from __future__ import annotations
import time
from textwrap import dedent
from app.config import settings

_started = time.time()

def uptime_human() -> str:
    sec = int(time.time() - _started)
    d, sec = divmod(sec, 86400)
    h, sec = divmod(sec, 3600)
    m, s = divmod(sec, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if s or not parts: parts.append(f"{s}s")
    return " ".join(parts)

def build_hq_message() -> str:
    lines = [
        "🛰 **HQ-сводка**",
        f"• **Bot**: ENV=`{settings.env}` MODE=`{settings.mode}` BUILD=`{settings.build_mark}`",
    ]

    sha = settings.render_git_commit
    if sha:
        lines.append(f"• **SHA**:`{sha}`")

    render_bits = []
    if settings.render_service:
        render_bits.append(f"svc=`{settings.render_service}`")
    if settings.render_instance:
        render_bits.append(f"inst=`{settings.render_instance}`")
    if settings.render_region:
        render_bits.append(f"region=`{settings.render_region}`")
    if render_bits:
        lines.append("• Render: " + " ".join(render_bits))

    lines.append(f"• Uptime: `{uptime_human()}`")

    # Подсказка где искать детальные отчёты (если у тебя есть daily/post-deploy)
    lines.append("• Отчёт: не найден (проверьте daily/post-deploy отчёты)")

    return dedent("\n".join(lines))
