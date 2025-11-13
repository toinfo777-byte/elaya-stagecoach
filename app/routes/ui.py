# app/routes/ui.py
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
              },
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
    # простая заглушка-страница, фронт берёт события из /api/timeline
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
        pre {
          background: #111;
          padding: 1rem;
          border-radius: 6px;
          overflow-x: auto;
        }
      </style>
    </head>
    <body>
      <h1>Таймлайн Элайи</h1>
      <p>Автообновление каждые 5 сек • <a href="/">назад</a></p>

      <pre id="events-box">{}</pre>

      <script>
        async function loadTimeline() {
          try {
            const res = await fetch("/api/timeline?limit=200");
            const data = await res.json();
            document.getElementById("events-box").textContent =
              JSON.stringify(data.events, null, 2);
          } catch (e) {
            document.getElementById("events-box").textContent = "Ошибка загрузки /api/timeline";
            console.error(e);
          }
        }

        loadTimeline();
        setInterval(loadTimeline, 5000);
      </script>
    </body>
    </html>
    """
