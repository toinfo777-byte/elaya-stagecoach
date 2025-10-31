import os, time
from fastapi import APIRouter

router = APIRouter()

_started = time.time()

@router.get("/healthz")
def healthz():
    # Простой ответ 200 для Render health check
    return {"ok": True, "uptime_s": int(time.time() - _started)}

@router.get("/render")
def render_info():
    # Полезные переменные от Render (если есть)
    return {
        "env": os.getenv("ENV"),
        "mode": os.getenv("MODE"),
        "build_mark": os.getenv("BUILD_MARK"),
        "render_git_commit": os.getenv("RENDER_GIT_COMMIT"),
        "render_service_id": os.getenv("RENDER_SERVICE_ID"),
        "port": os.getenv("PORT"),
    }
