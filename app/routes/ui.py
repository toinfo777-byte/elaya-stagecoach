from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])

@router.get("/", response_class=HTMLResponse)
def home():
    return "<h1>Элайя — StageCoach</h1><p>Портал онлайн. Проверь /healthz и /api/status.</p>"

@router.get("/healthz")
def healthz():
    return {"status": "ok"}
