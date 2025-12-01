from __future__ import annotations

from fastapi import FastAPI
from app.routes import router as routes_router

app = FastAPI(title="Elaya Core", version="0.1.0")

# Подключаем все маршруты (/api/sync, /api/progress, и т.п.)
app.include_router(routes_router)
