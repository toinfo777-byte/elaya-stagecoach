from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()  # ВАЖНО: без prefix здесь, он ставится в main.py

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/healthz")
def healthz():
    return {"status": "ok"}

@router.get("/status")
def status():
    return {
        "ok": True,
        "core": {"cycle": 0, "last_update": "-", "intro": 0, "reflect": 0, "transition": 0, "events": []},
        "ts": datetime.now(timezone.utc).isoformat()
    }
