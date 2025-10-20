# Elaya DevOps Runbook — Q4 2025

## Контур
GitHub → Actions → GHCR → Render → Telegram  
Наблюдаемость: Render Logs, Sentry, Cronitor/Healthchecks.

## Ветки и окружения
- `develop` → образ `:develop` → Render service `elaya-stagecoach-bot` (dev)
- (опц.) `staging` → образ `:staging` → Render service `elaya-stagecoach-bot-stg`

## Секреты и ENV
**GitHub Secrets**: `RENDER_DEPLOY_HOOK`, `TELEGRAM_TOKEN`, `ADMIN_ALERT_CHAT_ID` (+ опц. Cronitor).  
**Render ENV**: `TELEGRAM_TOKEN`, `ENV`, `SENTRY_DSN`, `CRONITOR_PING_URL/HEALTHCHECKS_URL`, `TZ_DEFAULT`,
`DB_URL`, `PROGRESS_DB`, `IMAGE_TAG`, `SHORT_SHA`, `BUILD_MARK`.

## Деплой
- Авто: push в `develop` → GHCR → Deploy Hook → Render рестартует воркер.
- Ручной: Render → “Manual Deploy”.

## Наблюдаемость
- `/status` у бота: BUILD_MARK, GIT_SHA, IMAGE_TAG, uptime, Sentry/Cronitor.
- Sentry: DSN в Render, стартовая «startup probe».
- Cronitor/HC: heartbeat по расписанию (опц.) или при старте.

## Отказоустойчивость
- Rollback: в Render указать предыдущий тег образа GHCR.
- Бэкапы: `scripts/sqlite_backup.sh` (cron/Pre-Deploy). VACUUM: `scripts/vacuum_sqlite.py`.

## Частые проблемы
- Команды «лежат»: проверить токен/логи Render, rate limits TG.
- Хук молчит: сверить URL в Secret `RENDER_DEPLOY_HOOK`.
- Метки пустые: шаг `Compute build meta` в Actions.
