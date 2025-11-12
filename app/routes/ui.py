from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def portal():
    return """
    <html>
      <head><title>Элайя — StageCoach</title></head>
      <body style='background:#0b0f14;color:#e5e7eb;font-family:sans-serif'>
        <h1>Элайя — StageCoach</h1>
        <p>Портал онлайн. Проверь <code>/healthz</code> и <code>/api/status</code>.</p>
      </body>
    </html>
    """
