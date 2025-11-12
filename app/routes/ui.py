def _html_page() -> str:
    return """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Элайя — StageCoach · Панель наблюдения</title>
  <style>
    :root {
      --bg:#0b0f14; --card:#121821; --text:#e6edf3; --muted:#9fb0c3;
      --accent:#ffd166; --ok:#2bd576;
    }
    * { box-sizing:border-box; }
    body {
      margin:0; font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto;
      background:var(--bg); color:var(--text); transition:background 1s ease;
    }
    .wrap { max-width:1100px; margin:32px auto; padding:0 16px; position:relative; }

    /* --- дыхание света --- */
    .pulse {
      position:fixed; bottom:28px; right:36px; width:22px; height:22px;
      border-radius:50%; background:radial-gradient(circle,var(--accent) 0%, transparent 70%);
      box-shadow:0 0 10px var(--accent);
      opacity:0.5; animation:pulse 8s ease-in-out infinite;
    }
    @keyframes pulse {
      0%   { transform:scale(0.7); opacity:0.4; }
      25%  { transform:scale(1); opacity:1; }
      50%  { transform:scale(1.2); opacity:0.6; }
      75%  { transform:scale(1); opacity:0.9; }
      100% { transform:scale(0.7); opacity:0.4; }
    }

    h1 { font-size:40px; letter-spacing:.3px; margin:0 0 16px; }
    .dot { color:var(--accent) }
    .grid { display:grid; gap:16px; grid-template-columns: 1fr; }
    @media (min-width:960px){ .grid { grid-template-columns:1.2fr .8fr; } }
    .card {
      background:var(--card); border:1px solid rgba(255,255,255,.06);
      border-radius:14px; padding:18px; position:relative;
      overflow:hidden;
    }
    .title { font-size:12px; letter-spacing:.16em; text-transform:uppercase; color:var(--muted); margin-bottom:8px; }
    .badges { display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 2px; }
    .badge {
      padding:6px 10px; border-radius:999px; background:#0f141c;
      border:1px solid rgba(255,255,255,.06); font-size:12px;
    }
    .btn {
      cursor:pointer; user-select:none; padding:10px 14px; border-radius:10px;
      border:1px solid rgba(255,255,255,.12); background:#0f141c; color:var(--text);
      font-weight:600; transition:background 0.3s ease;
    }
    .btn:hover { background:#121a24; }
    .muted { color:var(--muted); }
    .row { display:flex; gap:12px; align-items:center; flex-wrap:wrap; }
    .mono { font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace; }
    .list { margin:8px 0 0; padding:0; list-style:none; }
    .list li { padding:8px 0; border-top:1px dashed rgba(255,255,255,.06); }
    .small { font-size:12px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Элайя — StageCoach <span class="dot">•</span></h1>

    <div class="grid">
      <div class="card">
        <div class="title">Портал</div>
        <div class="badges">
          <span class="badge">Stable</span>
          <span class="badge">Online</span>
          <span class="badge">Light active</span>
        </div>
        <div class="row" style="margin-top:10px">
          <button class="btn" id="syncBtn">Синхронизировать</button>
          <span class="muted small">вдохни ядро и обнови состояние</span>
        </div>
        <div style="margin-top:16px">
          <div class="title">Core • состояние</div>
          <div class="mono" id="coreState">—</div>
        </div>
      </div>

      <div class="card">
        <div class="title">Журнал событий</div>
        <ul class="list mono small" id="eventsList">
          <li class="muted">загрузка…</li>
        </ul>
      </div>
    </div>

    <div class="card" style="margin-top:16px">
      <div class="title">API</div>
      <div class="mono small">
        GET <span class="muted">/api/status</span> · POST <span class="muted">/api/sync</span> · GET <span class="muted">/healthz</span>
      </div>
    </div>
  </div>

  <div class="pulse" title="дыхание ядра"></div>

  <script>
    const $core = document.getElementById('coreState');
    const $events = document.getElementById('eventsList');
    const $btn = document.getElementById('syncBtn');
    const $pulse = document.querySelector('.pulse');

    async function loadStatus() {
      const res = await fetch('/api/status', {cache:'no-store'});
      const data = await res.json();
      const s = data.core;
      $core.textContent = JSON.stringify({
        cycle: s.cycle,
        last_update: s.last_update,
        intro: s.intro, reflect: s.reflect, transition: s.transition
      }, null, 2);

      $events.innerHTML = '';
      if (!s.events || !s.events.length) {
        $events.innerHTML = '<li class="muted">нет событий</li>';
      } else {
        for (const e of s.events.slice(0, 8)) {
          const li = document.createElement('li');
          li.textContent = `[${e.ts}] ${e.kind}: ${JSON.stringify(e.payload)}`;
          $events.appendChild(li);
        }
      }
    }

    async function sync() {
      $btn.disabled = true;
      $pulse.style.boxShadow = "0 0 30px var(--ok)";
      try {
        await fetch('/api/sync', {method:'POST'});
        await loadStatus();
      } finally {
        $pulse.style.boxShadow = "0 0 10px var(--accent)";
        $btn.disabled = false;
      }
    }

    $btn.addEventListener('click', sync);
    loadStatus();
    setInterval(loadStatus, 20000);
  </script>
</body>
</html>
    """
