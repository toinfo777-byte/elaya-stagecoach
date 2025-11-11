from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import sqlite3
import os

# — если у тебя уже есть Templates в другом месте — можешь переиспользовать
templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/ui", tags=["ui"])

# путь к SQLite (так же, как в app/core/store.py)
DB_URL = os.getenv("DB_URL", "sqlite:////data/elaya.db")
def _db_path_from_url(url: str) -> str:
    return url.replace("sqlite:///", "/", 1) if url.startswith("sqlite:") else url
DB_PATH = _db_path_from_url(DB_URL)

def _read_stats() -> dict:
    intro = reflect = transition = 0
    users = 0
    last_updated = None
    last_reflection = None

    if not os.path.exists(DB_PATH):
        return {
            "users": 0,
            "last_updated": None,
            "counts": {"intro": 0, "reflect": 0, "transition": 0},
            "last_reflection": None,
        }

    with sqlite3.connect(DB_PATH) as con:
        # количество уникальных пользователей
        cur = con.execute("SELECT COUNT(*) FROM scene_state")
        users = cur.fetchone()[0] or 0

        # счётчики по сценам
        cur = con.execute(
            "SELECT last_scene, COUNT(*) FROM scene_state GROUP BY last_scene"
        )
        for last_scene, cnt in cur.fetchall():
            if last_scene == "intro":
                intro = cnt
            elif last_scene == "reflect":
                reflect = cnt
            elif last_scene == "transition":
                transition = cnt

        # последнее обновление
        cur = con.execute(
            "SELECT MAX(updated_at) FROM scene_state"
        )
        last_updated = cur.fetchone()[0]

        # последняя рефлексия (самая свежая непустая last_reflect)
        cur = con.execute(
            "SELECT last_reflect FROM scene_state "
            "WHERE last_reflect IS NOT NULL AND TRIM(last_reflect) <> '' "
            "ORDER BY updated_at DESC LIMIT 1"
        )
        row = cur.fetchone()
        last_reflection = row[0] if row else None

    return {
        "users": users,
        "last_updated": last_updated,
        "counts": {"intro": intro, "reflect": reflect, "transition": transition},
        "last_reflection": last_reflection,
    }

@router.get("/ping")
async def ui_ping():
    return {"ui": "ok", "ts": datetime.utcnow().isoformat() + "Z"}

@router.get("/stats.json")
async def ui_stats_json():
    return JSONResponse(_read_stats())

@router.get("/", response_class=HTMLResponse)
async def ui_index(request: Request):
    # можно сразу отдать начальные данные — страница всё равно будет автообновляться
    stats = _read_stats()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stats": stats,
        },
    )
