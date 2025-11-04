#!/usr/bin/env bash
set -euo pipefail

: "${TELEGRAM_TOKEN:?TELEGRAM_TOKEN is required}"

curl -sS "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo" | jq .
