from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Главная (рендер панели)
@router.get("/")
def index(request: Request):
    # Можно передать любые данные в шаблон:
    ctx = {
        "request": request,
        "title": "Элайя — StageCoach",
        "version": "1.2",
        "portal_flags": ["Stable", "Online", "Light active"],
        "hello_text": "Привет! Панель Элайи запущена.",
    }
    return templates.TemplateResponse("index.html", ctx)

# Пинг для UI
@router.get("/ui/ping")
def ui_ping():
    return {"ui": "ok"}

# Мини-статистика для карточек
@router.get("/ui/stats.json")
def ui_stats():
    # Заглушка — сюда потом подставим реальные счётчики из БД
    data = {
        "core": {
            "users": 0,
            "intro": 0,
            "reflect": 0,
            "transition": 0,
            "last_updated": "",
        },
        "reflection": {
            "text": "",
            "updated_at": "",
        },
        "status": "ok",
    }
    return JSONResponse(data)
