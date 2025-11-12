import os
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, Depends

router = APIRouter(prefix="/api", tags=["api"])

# простое локальное состояние (если позже будет StateStore — легко заменить)
CORE = {
    "cycle": 0,
    "last_update": "-",
    "intro": 0,
    "reflect": 0,
    "transition": 0,
    "events": [],
}

GUARD_KEY = os.getenv("GUARD_KEY", "")

def guard_dep(request: Request):
    # если GUARD_KEY задан в окружении — требуем совпадение заголовка
    if GUARD_KEY:
        provided = request.headers.get("x-guard-key", "")
        if provided != GUARD_KEY:
            raise HTTPException(status_code=403, detail="Forbidden")

@router.get("/status")
def status():
    # отдаём только последние 10 событий, чтобы не разрасталось
    core = dict(CORE)
    core["events"] = core["events"][-10:]
    return {"ok": True, "core": core}

@router.post("/sync")
def sync(payload: dict | None = None, _guard: None = Depends(guard_dep)):
    source = (payload or {}).get("source", "unknown")
    CORE["cycle"] += 1
    CORE["last_update"] = datetime.now(timezone.utc).isoformat()
    CORE["events"].append({"source": source, "cycle": CORE["cycle"]})
    return {"ok": True, "core": CORE}
