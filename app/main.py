from fastapi import FastAPI
from app.routes.system import router as system_router  # <- важно: папка/имя

app = FastAPI(title="Elaya StageCoach Web")

# базовые роуты для healthcheck и статуса
app.include_router(system_router, prefix="")

@app.get("/")
async def root():
    return {"ok": True, "app": "elaya-stagecoach-web"}
