from fastapi import FastAPI
from app.routes import system, ui

app = FastAPI(title="elaya-stagecoach-web")

# API без внутреннего prefix в самом роутере — вешаем здесь
app.include_router(system.router, prefix="/api", tags=["api"])

# UI/страницы
app.include_router(ui.router, tags=["ui"])
