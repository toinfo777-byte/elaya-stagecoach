from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import system as system_router
from app.routes import ui as ui_router
from app.routes import api as api_router

app = FastAPI(title="Elaya — StageCoach", version="1.2")

# CORS — на будущее (можно убрать)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(system_router.router, tags=["system"])
app.include_router(api_router.router, prefix="/api", tags=["api"])
app.include_router(ui_router.router, tags=["ui"])
