# app/main.py
from fastapi import FastAPI
from app.routes import system as system_router
from app.routes import ui as ui_router

app = FastAPI(title="Elaya StageCoach")

# system: /health, /healthz, /api/...
app.include_router(system_router.router, tags=["system"])
# ui: /
app.include_router(ui_router.router, tags=["ui"])
