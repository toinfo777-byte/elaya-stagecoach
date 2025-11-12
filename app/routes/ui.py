from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])

HTML = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Элайя — StageCoach</title>
  <style>
    body{background:#0b0f14;color:#eaeef2;font:16px/1.5 system-ui, -apple-system, Segoe UI, Roboto, sans-serif;margin:0}
    main{max-width:960px;margin:48px auto;padding:0 20px}
    h1{font-weight:800;letter-spacing:.2px;margin:0 0 8px}
    .muted{opacity:.75}
    .row{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
    button{padding:10px 14px;border:0;border-radius:10px;background:#1f6feb;color:#fff;font-weight:700;cursor:pointer}
    button.ghost{background:#161b22;color:#eaeef2}
    pre{background:#0e1116;border:1px solid #1d2633;padding:12px;border-radius:10px;overflow:auto}
    input{padding:10px 12px;border-radius:10px;border:1px solid #1d2633;background:#0e1116;color:#eaeef2}
    small{opacity:.7}
  </style>
</head>
<body>
  <main>
    <h1>Элайя — <span>StageCoach</span> <b class="dot"></b></h1>
    <p class="muted">Панель наблюдения. Проверь <code>/healthz</code> и <code>/api/status</code>.</p>

    <div class="row" style="margin-top:18px;">
      <button id="syncBtn">Синхронизировать</button>
      <button id="refreshBtn" class="ghost">Обновить статус</button>
      <small>использует <code>POST /api/sync</code> и затем <code>GET /api/status</code></small>
    </div>

    <div class="row" style="margin-top:10px;gap:8px">
      <input id="guardInput" placeholder="X-Guard-Key…" style="min-width:260px" />
      <button id="saveGuard" class="ghost">Сохранить ключ</button>
      <small>ключ хранится в <code>localStorage</code> и уходит заголовком <code>X-Guard-Key</code></small>
    </div>

    <h3 style="margin:24px 0 8px">Core • состояние</h3>
    <pre id="core">{ "cycle": 0, "last_update": "-", "intro": 0, "reflect": 0, "transition": 0, "events": [] }</pre>
  </main>

  <script>
    const $ = (q) => document.querySelector(q);

    function getGuard() {
      return localStorage.getItem("guardKey") || "";
    }
    function setGuard(v) {
      localStorage.setItem("guardKey", v || "");
      $("#guardInput").value = getGuard();
    }

    async function loadStatus() {
      const r = await fetch("/api/status", {cache:"no-store"});
      const j = await r.json();
      $("#core").textContent = JSON.stringify(j.core, null, 2);
    }

    $("#syncBtn").onclick = async () => {
      const hdrs = { "Content-Type":"application/json" };
      const key = getGuard();
      if (key) hdrs["X-Guard-Key"] = key;

      const r = await fetch("/api/sync", {
        method: "POST",
        headers: hdrs,
        body: JSON.stringify({ source: "ui" })
      });
      if (!r.ok) {
        const txt = await r.text();
        alert("Sync error: " + r.status + " " + txt);
        return;
      }
      await loadStatus();
    };

    $("#refreshBtn").onclick = loadStatus;
    $("#saveGuard").onclick = () => setGuard($("#guardInput").value);

    // init
    $("#guardInput").value = getGuard();
    loadStatus();
  </script>
</body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
def home():
  return HTML

@router.get("/healthz")
def healthz():
  return {"status": "ok"}
