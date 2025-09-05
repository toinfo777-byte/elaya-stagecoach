#!/usr/bin/env bash
set -euo pipefail

SRC="/data/elaya.db"          # путь к твоей SQLite-базе (должен совпадать с DB_URL)
DST="/data/backups"
STAMP="$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "$DST"
cp -f "$SRC" "$DST/elaya-${STAMP}.db"

# храним бэкапы 7 дней
find "$DST" -name 'elaya-*.db' -type f -mtime +7 -delete

echo "backup: $DST/elaya-${STAMP}.db"
