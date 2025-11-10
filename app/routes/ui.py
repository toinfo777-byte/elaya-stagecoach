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
      <head>
        <title>{meta.name}</title>
        <style>
          body {{
            background:{bg};
            color:{fg};
            font-family:Inter, sans-serif;
            text-align:center;
            padding-top:10%;
          }}
          h1 {{ font-size:3em; letter-spacing:.05em; }}
          p  {{ opacity:.8; font-size:1.2em; }}
        </style>
      </head>
      <body>
        <h1>{meta.name}</h1>
        <p>{meta.motto}</p>
        <p style='margin-top:3em;'>HQ Panel · Year {meta.get("identity","year")}</p>
      </body>
    </html>
    """
