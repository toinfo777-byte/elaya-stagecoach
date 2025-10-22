# app/routers/diag.py
from fastapi import APIRouter, Request, HTTPException
from datetime import datetime, timezone
import os

router = APIRouter()

STATUS_KEY = os.getenv("STATUS_KEY", "")  # опционально

def _bool_env(name: str, default: bool = True) -> bool:
    val = os.getenv(name)
    if val is None: 
        return default
    return val.lower() not in {"0", "false", "no"}

@router.get("/status_json")
async def status_json(request: Request, key: str | None = None):
    # Простейшая "защита" ключом (по желанию)
    if STATUS_KEY and key != STATUS_KEY:
        raise HTTPException(status_code=403, detail="forbidden")

    # эти поля подставь из своих реальных источников
    data = {
        "env": os.getenv("ENV", "develop"),
        "build_mark": os.getenv("BUILD_MARK", "deploy-unknown"),
        "git_sha": os.getenv("GIT_SHA", "")[:7],
        "image": os.getenv("IMAGE", "ghcr.io/<owner>/<repo>:develop"),
        "render_status": "live",                     # можешь дергать Render API, если хочешь
        "sentry_ok": _bool_env("SENTRY_OK", True),   # или проверь sentry init/last_event_id
        "cronitor_ok": _bool_env("CRONITOR_OK", True),
        "cronitor_last_ping_iso": os.getenv("CRONITOR_LAST_PING_ISO", ""),
        "bot_time_iso": datetime.now(timezone.utc).isoformat(),
        "uptime_sec": int(float(os.getenv("UPTIME_SEC", "0"))),
    }
    return data
