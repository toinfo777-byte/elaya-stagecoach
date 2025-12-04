# app/main.py
from __future__ import annotations

from fastapi import FastAPI

from app.routes import router as routes_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Elaya Core",
        version="0.1.0",
    )

    # подключаем все маршруты из app/routes/__init__.py
    app.include_router(routes_router)

    return app


app = create_app()
