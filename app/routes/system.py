import os
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, Depends

router = APIRouter(prefix="/api", tags=["api"])

# --- ядро Элайи ---
CORE = {
    "cycle": 0,
    "last_update": "-",
    "intro": 0,
    "reflect": 0,
    "transition": 0,
    "events": [],
    "reflection": {"text": "", "updated_at": "-"},
}

GUARD_KEY = os.getenv("GUARD_KEY", "")

# --- защита API ---
def guard_dep(request: Request):
    if GUARD_KEY:
        provided = request.headers.get("x-guard-key", "")
        if provided != GUARD_KEY:
            raise HTTPException(status_code=403, detail="Forbidden")

# --- базовые эндпоинты ---
@router.get("/status")
def status():
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

# --- модуль отражений (reflection) ---
@router.post("/reflection")
def reflection(payload: dict, _guard: None = Depends(guard_dep)):
    """Добавляет заметку в ядро Элайи."""
    text = payload.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty reflection")

    CORE["reflect"] += 1
    CORE["reflection"] = {
        "text": text,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    CORE["events"].append({
        "source": "reflection",
        "cycle": CORE["cycle"],
        "text": text,
    })
    return {"ok": True, "reflection": CORE["reflection"]}
