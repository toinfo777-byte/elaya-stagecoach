from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])


@router.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!doctype html>
    <html lang="ru">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <title>Элайя — StageCoach</title>
      <link rel="stylesheet" href="https://unpkg.com/sakura.css/css/sakura-dark.css" />
      <style>
        body { max-width: 960px; margin: 0 auto; }
        pre {
          background: #111;
          padding: 1rem;
          border-radius: 6px;
          overflow-x: auto;
        }
        .toolbar {
          margin-top: 1rem;
          display: flex;
          flex-wrap: wrap;
          gap: .5rem;
        }
        button {
          cursor: pointer;
        }
        .small { font-size: .8rem; opacity: .8; }
      </style>
    </head>
    <body>
      <h1>Элайя — <span>StageCoach</span></h1>
      <p>Панель наблюдения. Проверь <code>/healthz</code> и <code>/api/status</code>.</p>

      <div class="toolbar">
        <a href="/timeline">Открыть таймлайн</a>
        <button id="btn-sync">Синхронизировать</button>
        <button id="btn-refresh">Обновить статус</button>
      </div>

      <p class="small">
        Ключ хранится в <code>localStorage</code> и уходит заголовком <code>X-Guard-Key</code>
      </p>

      <pre id="core-box">{}</pre>

      <h2>Последняя заметка</h2>
      <pre id="reflection-box">{}</pre>

      <script>
        const STORAGE_KEY = "elaya_guard_key";

        function getGuardKey() {
          return localStorage.getItem(STORAGE_KEY) || "";
        }

        async function loadStatus() {
          try {
            const res = await fetch("/api/status");
            const data = await res.json();
            document.getElementById("core-box").textContent =
              JSON.stringify(data.core, null, 2);

            const refl = data.core.reflection || {text: "", updated_at: "-"};
            document.getElementById("reflection-box").textContent =
              JSON.stringify(refl, null, 2);
          } catch (e) {
            document.getElementById("core-box").textContent = "Ошибка загрузки /api/status";
            console.error(e);
          }
        }

        async function syncCore() {
          try {
            const key = getGuardKey();
            const res = await fetch("/api/sync", {
              method: "POST",
              headers: {
                "X-Guard-Key": key || "",
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                source: "ui",
                scene: "transition",
                payload: {
                  note: "manual sync from UI"
                }
              })
            });
            const data = await res.json();
            document.getElementById("core-box").textContent =
              JSON.stringify(data.core, null, 2);
          } catch (e) {
            console.error(e);
          }
        }

        document.getElementById("btn-refresh").addEventListener("click", loadStatus);
        document.getElementById("btn-sync").addEventListener("click", syncCore);

        // первичная загрузка
        loadStatus();
      </script>
    </body>
    </html>
    """


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/timeline", response_class=HTMLResponse)
async def timeline_page():
    # UI для структурированного таймлайна
    return """
    <!doctype html>
    <html lang="ru">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <title>Элайя — Timeline</title>
      <link rel="stylesheet" href="https://unpkg.com/sakura.css/css/sakura-dark.css" />
      <style>
        body { max-width: 960px; margin: 0 auto; }
        .timeline {
          list-style: none;
          margin: 0;
          padding: 0;
        }
        .item {
          padding: 0.6rem 0.8rem;
          border-radius: 8px;
          margin-bottom: 0.4rem;
          background: rgba(15, 23, 42, 0.9);
          border: 1px solid rgba(55, 65, 81, 0.7);
        }
        .meta {
          font-size: 0.8rem;
          margin-bottom: 0.2rem;
          display: flex;
          justify-content: space-between;
          gap: 0.5rem;
        }
        .badges {
          display: flex;
          gap: 0.25rem;
          flex-wrap: wrap;
        }
        .badge {
          font-size: 0.75rem;
          padding: 0.05rem 0.4rem;
          border-radius: 999px;
          border: 1px solid rgba(148, 163, 184, 0.7);
        }
        .note {
          font-size: 0.85rem;
        }
        .ts {
          color: #9ca3af;
        }
        .small {
          font-size: 0.8rem;
          opacity: 0.8;
        }
      </style>
    </head>
    <body>
      <h1>Таймлайн Элайи</h1>
      <p class="small">Автообновление каждые 5 сек • <a href="/">назад</a></p>

      <ul id="timeline" class="timeline"></ul>

      <script>
        async function loadTimeline() {
          try {
            const res = await fetch("/api/timeline?limit=200");
            const data = await res.json();
            const events = data.events || [];
            const list = document.getElementById("timeline");
            list.innerHTML = "";

            for (const e of events) {
              const li = document.createElement("li");
              li.className = "item";

              const ts = e.ts || "";
              const source = e.source || "system";
              const scene = e.scene || "other";
              const cycle = e.cycle ?? 0;
              const payload = e.payload || {};
              const note = payload.note || "";

              li.innerHTML = `
                <div class="meta">
                  <span class="ts">${ts}</span>
                  <div class="badges">
                    <span class="badge">src: ${source}</span>
                    <span class="badge">scene: ${scene}</span>
                    <span class="badge">cycle: ${cycle}</span>
                  </div>
                </div>
                <div class="note">${note || "<i>нет заметки</i>"}</div>
              `;

              list.appendChild(li);
            }
          } catch (e) {
            console.error(e);
          }
        }

        loadTimeline();
        setInterval(loadTimeline, 5000);
      </script>
    </body>
    </html>
    """
