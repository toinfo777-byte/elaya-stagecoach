from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import ui as ui_routes
from app.routers import system as system_routes

app = FastAPI(title="Elaya StageCoach Web")

# статика и шаблоны
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# роуты
app.include_router(system_routes.router, prefix="/diag", tags=["diag"])
app.include_router(ui_routes.router, tags=["ui"])

# корень = панель
@app.get("/")
async def root():
    return await ui_routes.index()
