from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(prefix="/api", tags=["api"])

CORE = {"cycle": 0, "last_update": "-", "intro": 0, "reflect": 0, "transition": 0, "events": []}

@router.get("/status")
def status():
    return {"ok": True, "core": CORE}

@router.post("/sync")
def sync():
    CORE["cycle"] += 1
    CORE["last_update"] = datetime.now(timezone.utc).isoformat()
    CORE["events"].append({"source": "ui", "cycle": CORE["cycle"]})
    return {"ok": True, "core": CORE}
