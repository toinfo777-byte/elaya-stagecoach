#!/usr/bin/env bash
set -euo pipefail

# По умолчанию
: "${MODE:=web}"
: "${PORT:=10000}"
: "${LOG_LEVEL:=info}"

# Приведём LOG_LEVEL к нижнему регистру (на всякий)
LOG_LEVEL="$(echo "$LOG_LEVEL" | tr '[:upper:]' '[:lower:]')"

echo "/////////////////////////////////////////////////////////////"
echo ">>> Elaya Stagecoach | MODE=${MODE}  PORT=${PORT}  LOG_LEVEL=${LOG_LEVEL}"
echo "/////////////////////////////////////////////////////////////"

case "$MODE" in
  web)
    # FastAPI (Uvicorn) — слушаем 0.0.0.0:$PORT (Render подставляет переменную PORT)
    exec uvicorn app.main:app \
      --host 0.0.0.0 \
      --port "${PORT}" \
      --log-level "${LOG_LEVEL}"
    ;;
  worker|polling)
    # Фоновый воркер (бот / любые джобы)
    exec python -m app.main
    ;;
  *)
    echo "Unknown MODE: ${MODE}. Falling back to 'web'."
    exec uvicorn app.main:app \
      --host 0.0.0.0 \
      --port "${PORT}" \
      --log-level "${LOG_LEVEL}"
    ;;
esac
