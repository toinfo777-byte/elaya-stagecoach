#!/usr/bin/env bash
set -euo pipefail

: "${TELEGRAM_TOKEN:?TELEGRAM_TOKEN is required}"

curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/deleteWebhook" \
  -d "drop_pending_updates=true" \
| jq .
