from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()


@router.get("/")
async def root():
    # редиректим на панель наблюдения
    return {"ok": True, "app": "elaya-stagecoach-web"}

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/healthz")
async def healthz():
    return {"status": "ok"}

@router.get("/status")
async def status():
    return {
        "service": "elaya-stagecoach-web",
        "version": "1.2",
        "time": datetime.now(timezone.utc).isoformat(),
    }

@router.get("/version")
async def version():
    return {"version": "1.2"}
