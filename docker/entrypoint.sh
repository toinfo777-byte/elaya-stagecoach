#!/usr/bin/env bash
set -e

MODE_ARG="${1:-web}"
MODE="${MODE:-$MODE_ARG}"

echo "[entrypoint] MODE=${MODE}"

if [ "$MODE" = "worker" ]; then
  # бот (polling/webhook — зависит от твоих настроек в коде)
  exec python -m app.main
elif [ "$MODE" = "web" ]; then
  # веб-сервис FastAPI
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
else
  echo "[entrypoint] Unknown MODE='$MODE' (use 'web' or 'worker')"
  exit 1
fi
