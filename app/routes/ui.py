from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home():
    # короткая заглушка UI
    return """
    <!doctype html>
    <html>
    <head><meta charset="utf-8"><title>Элайя — StageCoach</title></head>
    <body style="background:#0b0f14;color:#e5e7eb;font-family:system-ui,Segoe UI,Roboto,Arial">
      <h1>Элайя — StageCoach • portal</h1>
      <p>UI online. Отклики API: <code>/healthz</code>, <code>/api/status</code></p>
    </body>
    </html>
    """
