from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/ui/ping")
async def ui_ping():
    return JSONResponse({"ui": "ok"})

@router.get("/ui/stats.json")
async def ui_stats():
    return JSONResponse({
        "status": "ok",
        "portal": "Elaya StageCoach",
        "metrics": {"visits": 12, "active_users": 3, "light": 42}
    })

@router.get("/", response_class=HTMLResponse)
async def ui_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
