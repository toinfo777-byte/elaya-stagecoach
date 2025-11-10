# app/routes/ui.py
from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime
from app.core.meta import meta
from app.core import store

router = APIRouter()

def _fmt_dt(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        # ожидаем ISO с Z
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return iso

@router.get("/", response_class=HTMLResponse)
async def index():
    colors = meta.palette or {}
    bg = colors.get("dark_core", "#0a0905")
    fg = colors.get("core_light", "#f7e8bb")
    halo = colors.get("halo_gold", "#fceaa7")
    deep = colors.get("deep_gold", "#d4b85a")

    stats = store.get_stats()
    users = stats.get("users", 0)
    last_updated = _fmt_dt(stats.get("last_updated"))
    scenes = stats.get("scene_counts", {})
    last_reflect = stats.get("last_reflect") or "—"

    name = meta.name or "Elaya — School of Theatre of Light"
    motto = meta.motto or "Свет различает. Тьма хранит. Мы — между."

    return f"""
    <html>
      <head>
        <meta charset="utf-8"/>
        <title>{name}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <style>
          :root {{
            --bg: {bg};
            --fg: {fg};
            --halo: {halo};
            --deep: {deep};
          }}
          * {{ box-sizing: border-box; }}
          html, body {{ height: 100%; margin: 0; }}
          body {{
            background: radial-gradient(60% 50% at 50% 35%, #111 0%, var(--bg) 60%, #000 100%);
            color: var(--fg);
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
            display: grid;
            place-items: center;
            padding: 24px;
          }}
          .card {{
            width: min(900px, 92vw);
            background: rgba(10, 9, 5, .55);
            border: 1px solid rgba(214, 191, 109, .25);
            border-radius: 20px;
            padding: 28px 28px 22px;
            box-shadow: 0 20px 60px rgba(0,0,0,.35);
          }}
          h1 {{
            margin: 0 0 6px;
            font-weight: 800;
            letter-spacing: .04em;
            text-align: center;
          }}
          .motto {{
            margin: 0 0 18px;
            opacity: .85;
            text-align: center;
          }}
          .pulse {{
            --size: 22px;
            width: var(--size);
            height: var(--size);
            border-radius: 50%;
            background: var(--fg);
            box-shadow:
              0 0 10px var(--fg),
              0 0 24px var(--halo),
              0 0 48px rgba(255, 230, 170, .35);
            margin: 14px auto 8px;
            animation: breathe 3.6s ease-in-out infinite;
          }}
          @keyframes breathe {{
            0%   {{ transform: scale(0.92); opacity: .88; }}
            50%  {{ transform: scale(1.06); opacity: 1;   }}
            100% {{ transform: scale(0.92); opacity: .88; }}
          }}
          .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
            margin-top: 14px;
          }}
          .tile {{
            padding: 14px 16px;
            border: 1px solid rgba(214, 191, 109, .2);
            border-radius: 14px;
            background: rgba(22, 18, 10, .35);
          }}
          .k {{ font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: #cdbf8a; }}
          .v {{ font-weight: 700; }}
          .muted {{ opacity: .75; }}
          .scenes {{ display: flex; gap: 14px; margin-top: 8px; flex-wrap: wrap; }}
          .badge {{
            padding: 6px 10px;
            border-radius: 999px;
            border: 1px solid rgba(214,191,109,.25);
            background: rgba(32, 26, 15, .35);
            font-weight: 700;
            font-size: 13px;
          }}
          .foot {{
            margin-top: 16px;
            padding-top: 10px;
            border-top: 1px dashed rgba(214,191,109,.25);
            font-size: 13px;
            text-align: center;
            color: #d5c99e;
          }}
          .reflect {{
            font-style: italic;
            line-height: 1.55;
          }}
          @media (max-width: 720px) {{
            .grid {{ grid-template-columns: 1fr; }}
          }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>{name}</h1>
          <p class="motto">{motto}</p>
          <div class="pulse" title="HQ Pulse — breathing"></div>

          <div class="grid">
            <div class="tile">
              <div class="k">Core · Состояние</div>
              <div class="v" style="margin-top:8px;">Пользователей в памяти: {users}</div>
              <div class="muted" style="margin-top:6px;">Последнее обновление: {last_updated}</div>
              <div class="scenes">
                <div class="badge">intro: {scenes.get('intro', 0)}</div>
                <div class="badge">reflect: {scenes.get('reflect', 0)}</div>
                <div class="badge">transition: {scenes.get('transition', 0)}</div>
              </div>
            </div>
            <div class="tile">
              <div class="k">Reflection · Последняя заметка</div>
              <div class="reflect" style="margin-top:8px;">{last_reflect}</div>
            </div>
          </div>

          <div class="foot">HQ Panel · Cycle Active · Memory Stable · Reflection On</div>
        </div>
      </body>
    </html>
    """
