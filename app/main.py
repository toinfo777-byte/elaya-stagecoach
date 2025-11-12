from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Elaya StageCoach", version="1.0")

# --- HEALTH CHECKS ---
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# --- STATUS API ---
@app.get("/api/status")
async def status():
    return {
        "ok": True,
        "core": {
            "cycle": 0,
            "last_update": datetime.utcnow().isoformat(),
            "intro": 0,
            "reflect": 0,
            "transition": 0,
        },
    }

# --- SAFE ROUTER IMPORTS ---
def _safe_include_routes():
    try:
        from app.routes.ui import router as ui_router
        app.include_router(ui_router, tags=["ui"])
        print("[BOOT] UI router attached.")
    except Exception as e:
        print(f"[BOOT] UI router not attached: {e}")

    try:
        from app.routes.system import router as system_router
        app.include_router(system_router, tags=["system"])
        print("[BOOT] System router attached.")
    except Exception as e:
        print(f"[BOOT] System router not attached: {e}")

_safe_include_routes()
