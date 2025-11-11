from __future__ import annotations

from fastapi import APIRouter, Response
from starlette.responses import HTMLResponse

router = APIRouter()


@router.get("/ui/ping")
async def ui_ping():
    return Response(content="ui: ok", media_type="text/plain")


@router.get("/", response_class=HTMLResponse)
async def index():
    html = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Elaya — School of Theatre of Light</title>
  <style>
    :root { color-scheme: dark; }
    body { margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif; background:#0a0a0a; color:#f6ead6; }
    .shell { max-width: 980px; margin: 72px auto; padding: 0 20px; }
    .panel { border: 1px solid rgba(246,234,214,.15); border-radius: 18px; padding: 24px; background: radial-gradient(1200px 420px at 50% -120px, rgba(246,234,214,.08), rgba(0,0,0,0)); }
    h1 { font-weight: 800; font-size: 40px; letter-spacing: .5px; text-align: center; margin: 0 0 12px; }
    .sub { text-align:center; opacity:.8; margin-bottom:28px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .card { border: 1px dashed rgba(246,234,214,.18); border-radius: 14px; padding: 16px; min-height: 120px; }
    .kvs { display:flex; gap:12px; flex-wrap:wrap; margin-top:8px; }
    .kv { padding: 8px 12px; border-radius: 999px; border: 1px solid rgba(246,234,214,.18); font-weight:700; }
    .muted { opacity:.75; }
    .last { white-space: pre-wrap; word-break: break-word; min-height: 48px; }
    footer { margin-top: 18px; text-align:center; opacity:.6; font-size: 13px; }
  </style>
</head>
<body>
  <div class="shell">
    <div class="panel">
      <h1>Elaya — School of Theatre of Light</h1>
      <div class="sub">Свет различает. Тьма хранит. Мы — между.</div>

      <div class="grid">
        <div class="card">
          <div class="muted">CORE · СОСТОЯНИЕ</div>
          <div style="margin-top:8px">
            Пользователей в памяти: <b><span id="usersCnt">0</span></b><br/>
            Последнее обновление: <span id="lastUpdated">—</span>
          </div>
          <div class="kvs" style="margin-top:10px">
            <div class="kv">intro: <span id="introCnt">0</span></div>
            <div class="kv">reflect: <span id="reflectCnt">0</span></div>
            <div class="kv">transition: <span id="transitionCnt">0</span></div>
          </div>
        </div>

        <div class="card">
          <div class="muted">REFLECTION · ПОСЛЕДНЯЯ ЗАМЕТКА</div>
          <div id="lastReflection" class="last" style="margin-top:10px">—</div>
        </div>
      </div>

      <footer>HQ Panel · Cycle Active · Memory Stable · Reflection On</footer>
    </div>
  </div>

  <!-- автообновление маленькой панели -->
  <script>
  async function refreshStats(){
    try{
      const r = await fetch('/ui/stats.json', {cache:'no-store'});
      if(!r.ok) return;
      const j = await r.json();

      const set = (id, v) => {
        const el = document.getElementById(id);
        if (el) el.textContent = v;
      };

      // поддержка как компактного, так и расширенного формата
      const counts = j.counts || j.scene_counts || {};
      set('introCnt', counts.intro ?? 0);
      set('reflectCnt', counts.reflect ?? 0);
      set('transitionCnt', counts.transition ?? 0);

      set('usersCnt', j.users ?? 0);
      set('lastUpdated', j.last_updated || j.last_update || '—');

      const lr = (j.last_reflection && (j.last_reflection.text ?? j.last_reflection))
                 || '—';
      set('lastReflection', (typeof lr === 'string' && lr.trim().length) ? lr : '—');
    } catch(e){
      // тихо
      console.warn('stats refresh failed', e);
    }
  }
  refreshStats();
  setInterval(refreshStats, 5000);
  </script>
</body>
</html>
    """
    return HTMLResponse(html)
