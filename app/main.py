# app/main.py
from __future__ import annotations

from fastapi import FastAPI

from app.routes import api, ui, system

app = FastAPI()

# --- роутеры веб-ядра ---

# API (если используешь)
app.include_router(api.router)

# системные /api-эндпоинты (таймлайн и т.п.)
app.include_router(system.router)

# UI-страницы
app.include_router(ui.router)
