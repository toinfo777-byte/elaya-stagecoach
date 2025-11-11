from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Роутеры
from app.routes.system import router as system_router
from app.routes.ui import router as ui_router

app = FastAPI(title="Elaya — StageCoach", version="1.2")

# 1) Системный роутер без префикса — /health и /healthz доступны на корне
app.include_router(system_router)

# 2) UI роутер под /ui
app.include_router(ui_router, prefix="/ui")

# 3) Статика/индекс (если есть папка app/static с index.html — отдадим её)
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

INDEX_FILE = STATIC_DIR / "index.html"

@app.get("/", response_class=HTMLResponse)
def index():
    if INDEX_FILE.exists():
        return INDEX_FILE.read_text(encoding="utf-8")
    # fallback, чтобы хоть что-то отдать
    return """<html><head><title>Elaya — StageCoach</title></head>
<body><h1>Elaya — StageCoach</h1><p>Portal is live.</p></body></html>"""
