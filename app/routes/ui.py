from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core import store

router = APIRouter(prefix="/ui", tags=["ui"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/ping")
def ping():
    return {"ui": "ok"}

@router.get("/stats.json")
def stats():
    counts = store.get_counts()
    last_ref = store.get_last_reflection()
    return JSONResponse({
        "core": counts,
        "reflection": last_ref or {"text": "", "updated_at": ""},
        "status": "ok"
    })

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    core = store.get_counts()
    reflection = store.get_last_reflection()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "core": core,
            "reflection": reflection,
        }
    )
