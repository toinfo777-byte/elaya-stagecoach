#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=/app

MODE="${MODE:-web}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-10000}"
WORKERS="${WORKERS:-1}"
LOG_LEVEL="${LOG_LEVEL:-info}"

echo ">>> Elaya Stagecoach | MODE=${MODE} ENV=${ENV:-develop} BUILD=${BUILD_SHA:-local} SHA=${RENDER_GIT_COMMIT:-manual}"

if [[ "$MODE" == "web" ]]; then
  # FastAPI (status/health + твои роутеры)
  exec uvicorn app.main:app --host "$HOST" --port "$PORT" --workers "$WORKERS" --log-level "$LOG_LEVEL"
elif [[ "$MODE" == "worker" || "$MODE" == "polling" ]]; then
  # Aiogram polling-воркер
  exec python -m app.main
else
  echo "Unknown MODE: '$MODE' (allowed: web | worker)"
  exit 1
fi
