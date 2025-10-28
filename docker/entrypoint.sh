#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=/app

MODE="${MODE:-web}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-10000}"
WORKERS="${WORKERS:-1}"
LOG_LEVEL="${LOG_LEVEL:-info}"

# uvicorn принимает только lower-case
LOG_LEVEL="$(echo "$LOG_LEVEL" | tr '[:upper:]' '[:lower:]')"

echo ">>> Elaya Stagecoach | MODE=${MODE} ENV=${ENV:-develop} BUILD=${BUILD_SHA:-local} SHA=${RENDER_GIT_COMMIT:-manual} | LOG_LEVEL=${LOG_LEVEL}"

if [[ "$MODE" == "web" ]]; then
  exec uvicorn app.main:app --host "$HOST" --port "$PORT" --workers "$WORKERS" --log-level "$LOG_LEVEL"
elif [[ "$MODE" == "worker" || "$MODE" == "polling" ]]; then
  exec python -m app.main
else
  echo "Unknown MODE: '$MODE' (allowed: web | worker)"
  exit 1
fi
