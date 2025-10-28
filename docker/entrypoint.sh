#!/usr/bin/env bash
set -e

: "${MODE:=web}"

if [[ "$MODE" == "web" ]]; then
  # Запуск FastAPI
  exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
elif [[ "$MODE" == "worker" ]]; then
  # Запуск бота (polling) — адаптируй команду под свой main
  exec python -m app.main
else
  echo "Unknown MODE=$MODE (expected 'web' or 'worker')"
  exit 1
fi
