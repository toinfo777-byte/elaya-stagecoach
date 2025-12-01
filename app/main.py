from __future__ import annotations

from fastapi import FastAPI

from app.routers import router as main_router

app = FastAPI()


# --- healthchecks -------------------------------------------------


@app.get("/healthz")
async def root_healthcheck() -> dict:
    """
    Простой healthcheck для локального запуска.
    """
    return {"status": "ok"}


@app.get("/api/healthz")
async def api_healthcheck() -> dict:
    """
    Healthcheck для Render (он ходит именно в /api/healthz).
    """
    return {"status": "ok"}


# --- маршруты ядра ------------------------------------------------


# Подключаем корневой роутер (внутри уже system/ui/api и т.д.)
app.include_router(main_router)
