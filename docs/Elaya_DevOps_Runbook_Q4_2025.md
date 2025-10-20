# Elaya — DevOps Runbook (Q4 2025)

Статус: активен · Обновляется автоматически по мере изменений пайплайна.

## Цепочка деплоя
GitHub → GHCR → Render (worker) → Telegram.

- **Build**: `.github/workflows/build-and-push-ghcr.yml`
  - Теги: `:develop` и `:${sha}`
  - Метки билда передаются как build-args в Dockerfile и вписаны в `/app/.env`:
    - `BUILD_MARK`, `SHORT_SHA`, `IMAGE_TAG`, `ENV`
- **Deploy**: Render Deploy Hook (секрет в GitHub)
- **Бот**: `/status` и `/diag` (Sentry/Cronitor)

## Наблюдаемость
- **Sentry** — при старте шлётся probe; алерты на ошибки.
- **Cronitor/Healthchecks** — пинг каждые 5 минут; алерт при пропаже >15 минут.
- **Render Logs** — журнал рестартов и хуков.

## Штабной ритм (Stage III)
- Ежедневно 09:00 MSK (`daily-report.yml`)
- Генератор: `tools/daily_report.py`
- Отчёты: `docs/elaya_status/Elaya_Status_YYYY-MM-DD.md`
- TG-уведомление в штаб-чат.
- Авто-PR `develop → main` с автосквошем (labels: `auto-merge`, `daily-report`).

## Ручной деплой (fallback)
1) `Actions → Build & Push Docker image to GHCR → Run workflow`
2) Проверить GHCR тег `:develop`, ивенты Render
3) В TG `/status` должны обновиться `BUILD_MARK` / `GIT_SHA`

## Секреты (источники правды)
- GitHub Secrets: `RENDER_DEPLOY_HOOK`, `TELEGRAM_TOKEN`, `ADMIN_ALERT_CHAT_ID`, `SENTRY_DSN` (если есть), `CRONITOR_PING_URL` или `HEALTHCHECKS_URL`.
- Render ENV: базовые переменные бота (без токенов в репозитории).

## Стандарты веток
- `develop` — рабочая ветка автодеплоя
- `main` — стабильная (получает авто-PR от расписаний)

## Частые вопросы
- **Почему `/status` показывает local?** Метки не передались как `build-args` → проверить шаг Build & Push.
- **Как откатиться?** В Render нажать *Rollback* на предыдущий live build.
- **Как обновить статусный документ?** `/sync` в бот → блок пишется в `docs/Elaya_Current_Status_Q4_2025.md`.
