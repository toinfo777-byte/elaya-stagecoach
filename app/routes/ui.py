# app/routes/ui.py
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.core.cycle_state import CycleState
from app.routes.system import TIMELINE  # <— берём события прямо из system

router = APIRouter(tags=["ui"])


def _render_timeline(events: List[Dict[str, Any]]) -> str:
    """
    Простая текстовая верстка таймлайна.
    """
    if not events:
        return "<p>Пока нет событий</p>"

    parts: List[str] = []
    for ev in events:
        ts = ev.get("ts", "-")
        source = ev.get("source", "")
        scene = ev.get("scene", "")
        payload = ev.get("payload", {})

        parts.append(
            f"""
            <div class="event">
              <div class="ts">{ts}</div>
              <div class="meta">{source} — {scene}</div>
              <pre class="payload">{payload}</pre>
            </div>
            """
        )

    return "\n".join(parts)


@router.get("/timeline", response_class=HTMLResponse)
def timeline_page() -> HTMLResponse:
    """
    Живая страница таймлайна Элайи.
    """
    # ядро (если нужно — можно расширить)
    core: Dict[str, Any] = {
        "events": [e.model_dump() for e in TIMELINE],
    }
    cycle_state = CycleState.from_core(core)
    events = core.get("events", [])

    body = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
      <meta charset="utf-8" />
      <title>Таймлайн Элайи</title>
      <style>
        body {{
          background: #050811;
          color: #f5f5f5;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          padding: 24px;
        }}
        h1 {{
          margin-bottom: 8px;
        }}
        .cycle-meta {{
          margin-bottom: 24px;
          font-size: 14px;
          color: #b0b8ff;
        }}
        .event {{
          margin-bottom: 16px;
          padding-bottom: 8px;
          border-bottom: 1px solid #22263a;
        }}
        .ts {{
          font-size: 13px;
          color: #9ca3af;
        }}
        .meta {{
          font-weight: 600;
          margin-top: 2px;
          margin-bottom: 4px;
        }}
        .payload {{
          margin: 0;
          font-size: 13px;
          color: #e5e7eb;
          background: #0b1020;
          padding: 6px 8px;
          border-radius: 4px;
          white-space: pre-wrap;
        }}
      </style>
    </head>
    <body>
      <h1>Таймлайн Элайи</h1>
      <div class="cycle-meta">
        Цикл: <strong>{cycle_state.cycle}</strong> ·
        Фаза: <strong>{cycle_state.phase}</strong> ·
        Обновлено: {cycle_state.updated_at}
      </div>

      {_render_timeline(events)}
    </body>
    </html>
    """

    return HTMLResponse(content=body)
