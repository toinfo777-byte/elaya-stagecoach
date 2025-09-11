#!/usr/bin/env bash
# Lightweight SQLite backup for Render cron.
# - Uses DB_PATH env var to locate SQLite file.
# - If DB is absent -> SKIP (exit 0) instead of failing.
# - Saves compressed copy to /tmp/backups.

set -euo pipefail

echo "==> Starting SQLite backup"

# -------- locate repo root (for logs only) --------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# -------- config --------
DB_PATH="${DB_PATH:-}"              # e.g. /opt/render/project/src/data/db.sqlite
OUT_DIR="/tmp/backups"
TS="$(date -u +'%Y%m%dT%H%M%SZ')"
OUT_RAW="${OUT_DIR}/sqlite_${TS}.db"
OUT_GZ="${OUT_RAW}.gz"

# If DB_PATH is not set or file missing — skip backup gracefully
if [[ -z "${DB_PATH}" ]]; then
  echo "WARN: DB_PATH env is not set. Nothing to back up. Skipping."
  exit 0
fi
if [[ ! -f "${DB_PATH}" ]]; then
  echo "WARN: DB file not found at '${DB_PATH}'. Skipping backup."
  exit 0
fi

# Ensure sqlite3 exists
if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "ERROR: sqlite3 is not installed in this image."
  exit 1
fi

mkdir -p "${OUT_DIR}"

echo "Backing up DB_PATH=${DB_PATH}"
sqlite3 "${DB_PATH}" ".backup '${OUT_RAW}'"

echo "Compressing ${OUT_RAW} -> ${OUT_GZ}"
gzip -f "${OUT_RAW}"

ls -lh "${OUT_GZ}" || true
echo "==> Backup completed successfully."
