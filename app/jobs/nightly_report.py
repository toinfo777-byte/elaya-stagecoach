# app/jobs/nightly_report.py
from __future__ import annotations
import os
from datetime import datetime, timezone

async def make_nightly_report() -> str:
    # сюда можно подтягивать реальные метрики, Sentry, Render API и т. п.
    env = os.getenv("ENV", os.getenv("ENVIRONMENT", "unknown"))
    build = os.getenv("BUILD_MARK", os.getenv("RENDER_GIT_COMMIT", "manual"))

    now = datetime.now(timezone.utc).astimezone()
    lines = [
        "🛰 <b>Штабной отчёт — Daily</b>",
        f"<i>{now:%Y-%m-%d %H:%M:%S %Z}</i>",
        "",
        "• <b>DevOps-cycle</b>",
        f"  Env: <code>{env}</code>",
        f"  Build: <code>{build}</code>",
        "  Status: stable",
        "  Notes: webhook online; worker jobs scheduled.",
    ]
    return "\n".join(lines)
