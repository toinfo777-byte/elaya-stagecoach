from fastapi import FastAPI
from app.routes import ui_router, system_router

app = FastAPI(title="Elaya — StageCoach")

app.include_router(ui_router)        # UI + /healthz + /
app.include_router(system_router)    # /api/status, /api/sync
