from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.core.meta import meta

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index():
    colors = meta.palette
    bg = colors.get("dark_core", "#000")
    fg = colors.get("core_light", "#fff")
    return f"""
    <html>
      <body style='background:{bg};color:{fg};font-family:Inter,sans-serif;text-align:center;padding-top:12%'>
        <h1>{meta.name}</h1>
        <p style='opacity:.8;font-size:1.2em'>{meta.motto}</p>
        <p>Year {meta.get("identity","year")}</p>
      </body>
    </html>
    """
