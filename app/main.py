from fastapi import FastAPI

from app.routes.ui import router as ui_router
from app.routes.system import router as system_router

app = FastAPI(title="Elaya — StageCoach")

app.include_router(ui_router)
app.include_router(system_router)
