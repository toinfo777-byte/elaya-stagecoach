#!/usr/bin/env bash
set -euo pipefail

: "${TELEGRAM_TOKEN:?TELEGRAM_TOKEN is required}"
: "${WEBHOOK_URL:?WEBHOOK_URL is required}"

ALLOWED_UPDATES=${ALLOWED_UPDATES:-'["message","edited_message","channel_post","edited_channel_post","callback_query"]}

curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook" \
  -d "url=${WEBHOOK_URL}" \
  -d "allowed_updates=${ALLOWED_UPDATES}" \
  -d "drop_pending_updates=false" \
| jq .
