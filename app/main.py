from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Роуты UI и, при необходимости, другие
from app.routes import ui  # <-- есть app/routes/ui.py

app = FastAPI(title="Elaya StageCoach · Web")

# Статика: /static/css/theme.css и др.
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем роутер UI (/, /ui/ping, /ui/stats.json)
app.include_router(ui.router, prefix="", tags=["ui"])

# --- опционально: health для Render ---
@app.get("/healthz")
def healthz():
    return {"ok": True}
