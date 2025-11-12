from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="elaya-stagecoach-web", version="1.2")

# 1) Всегда доступный healthz для Render (даже если роутеры упадут)
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

# 2) Лёгкий статус ядра (можно расширять)
@app.get("/api/status")
async def api_status():
    return {"ok": True, "core": {"cycle": 0, "last_update": "-", "intro": 0, "reflect": 0, "transition": 0, "events": []}}

# 3) Подключаем UI/прочие роуты без падения приложения
def _safe_include_routes():
    try:
        # Вариант А: если в ui.py экспортируется `router`
        from app.routes.ui import router as ui_router
        app.include_router(ui_router, tags=["ui"])
    except Exception as e:
        print(f"[BOOT] ui router not attached: {e!r}")

    try:
        # Если есть system.py с `router`, подключим его так же.
        from app.routes.system import router as system_router
        app.include_router(system_router, tags=["system"])
    except Exception as e:
        print(f"[BOOT] system router not attached: {e!r}")

_safe_include_routes()
