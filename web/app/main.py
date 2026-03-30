# web/app/main.py
from __future__ import annotations

import logging

from fastapi import FastAPI

from app.routes.system import router as api_router

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="Elaya StageCoach Web(Core)", version="0.5.x")
    app.include_router(api_router)
    return app


app = create_app()
