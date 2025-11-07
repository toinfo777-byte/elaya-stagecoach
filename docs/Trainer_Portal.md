# Trainer как тонкий портал

**Идея.** Telegram — только «окно». Вся логика сцен живёт в веб-ядре (FastAPI). Trainer передаёт события в ядро и возвращает ответы.

## Контракт Core API
- `POST /api/scene/enter` → { reply }
- `POST /api/scene/reflect` → { reply }
- `POST /api/scene/transition` → { reply }
Хедер: `X-Core-Token: <CORE_API_TOKEN>`

## ENV
- Web: `MODE=web`, `CORE_API_TOKEN=<...>`
- Trainer: `BOT_PROFILE=trainer`, `CORE_API_BASE=<web_url>`, `CORE_API_TOKEN=<...>`, `SAFE_MODE=true`

## Приёмка (DoD)
- `/start` и обычные сообщения отзываются через ядро.
- В логах web видны вызовы `/api/scene/*`.
- 5xx и таймаутов нет; fallback-сообщение при сбое есть.
- HQ остаётся в SAFE MODE.
