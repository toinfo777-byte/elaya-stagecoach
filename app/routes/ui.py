# app/routes/ui.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def dashboard():
    # можно оставить простой минимал, главное — вернуть HTML
    return """
    <!doctype html>
    <html><head><meta charset="utf-8"><title>Элайя — StageCoach</title></head>
    <body style="font-family:system-ui;background:#0b0f14;color:#e6edf3">
      <h1>Элайя — StageCoach • UI</h1>
      <p>Портал онлайн. Проверь <a href="/healthz">/healthz</a> или статус API: <a href="/api/status">/api/status</a>.</p>
    </body></html>
    """
