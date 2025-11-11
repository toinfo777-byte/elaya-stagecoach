from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# простая "память" процесса (достаточно для MVP панели)
CORE = {
    "users": 0,
    "intro": 0,
    "reflect": 0,
    "transition": 0,
    "last_updated": ""
}
REFLECTION = {"text": "", "updated_at": ""}

def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

@router.get("/ui/ping")
async def ui_ping():
    return {"ui": "ok"}

@router.get("/ui/stats.json")
async def ui_stats():
    # отдаём структуру, которой пользуется фронт
    return {
        "core": CORE,
        "reflection": REFLECTION,
        "status": "ok"
    }

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "version": "1.2",
        },
    )

@router.post("/ui/reflection", response_class=JSONResponse)
async def add_reflection(text: str = Form(...)):
    REFLECTION["text"] = text.strip()
    REFLECTION["updated_at"] = _utc_now()
    CORE["last_updated"] = REFLECTION["updated_at"]
    return {"ok": True, "saved_at": REFLECTION["updated_at"]}
