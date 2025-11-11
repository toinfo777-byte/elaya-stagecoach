from fastapi import FastAPI
from app.routers import system
from app.routes import ui

app = FastAPI(title="Elaya StageCoach Web")

app.include_router(system.router, prefix="/diag", tags=["diag"])
app.include_router(ui.router, tags=["ui"])

@app.get("/")
async def root():
    return {"ok": True}
