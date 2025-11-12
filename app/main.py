from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(title="elaya-stagecoach-web")

# системные эндпоинты
from app.routes.system import router as system_router  # noqa: E402
app.include_router(system_router)

# (опционально) если появятся дополнительные роутеры — подключай безопасно
try:
    from app.routes.ui import router as ui_router  # пример
    app.include_router(ui_router)
except Exception:
    pass

@app.get("/")
async def root():
    return {"ok": True, "app": "elaya-stagecoach-web", "ts": datetime.now(timezone.utc).isoformat()}
