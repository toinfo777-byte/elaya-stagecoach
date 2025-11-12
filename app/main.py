from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.ui import router as ui_router
from app.routes.system import router as system_router

app = FastAPI(title="Elaya — StageCoach")

# маршруты приложения
app.include_router(ui_router)
app.include_router(system_router)

# статика: CSS, иконки и т.п.
# папка: app/static  → доступна по URL /static/...
app.mount("/static", StaticFiles(directory="app/static"), name="static")
