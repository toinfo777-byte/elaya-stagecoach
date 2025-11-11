from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/healthz")
async def healthz():
    # Render может пинговать разные урлы — пусть оба отвечают
    return {"status": "ok"}

@router.get("/status")
async def status():
    return {
        "service": "elaya-stagecoach-web",
        "version": "1.2",
        "time": datetime.now(timezone.utc).isoformat()
    }

@router.get("/version")
async def version():
    return {"version": "1.2"}

@router.post("/echo")
async def echo(payload: dict):
    return {"received": payload, "ok": True}
