from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.routes.system import timeline_events

router = APIRouter(tags=["ui"])

@router.get("/timeline", response_class=HTMLResponse)
async def timeline_page(request: Request):
    html = """
    <html>
        <head>
            <meta charset="utf-8">
            <title>Таймлайн Элайи</title>
        </head>
        <body style="background:#0b0f17; color:white; font-family:Arial;">
            <h1>Таймлайн Элайи</h1>
            %EVENTS%
        </body>
    </html>
    """

    if not timeline_events:
        events_html = "<p>Пока нет событий</p>"
    else:
        rows = []
        for e in reversed(timeline_events):
            rows.append(
                f"<div style='margin:10px 0; padding:10px; border:1px solid #333;'>"
                f"<b>{e.get('scene')}</b><br>"
                f"<small>{e.get('timestamp')}</small><br>"
                f"<pre>{e.get('payload')}</pre>"
                f"</div>"
            )
        events_html = "\n".join(rows)

    return html.replace("%EVENTS%", events_html)
