#!/usr/bin/env bash
# scripts/backup.sh
# Robust SQLite backup for Render cron job.
# Writes to /tmp/backups (writable on Render) and optionally uploads to S3.
# Exit codes: 0 OK, !=0 error.

set -euo pipefail

echo "==> Starting SQLite backup"

# ----- locate repo root -----
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# ----- config -----
# Provide DB path explicitly via env DB_PATH if you know it.
# Otherwise we'll try to auto-detect the first *.db file under repo.
DB_PATH="${DB_PATH:-}"

if [[ -z "${DB_PATH}" ]]; then
  # common locations
  CANDIDATES=(
    "data/app.db"
    "app.db"
    "db.sqlite3"
    "app/storage/app.db"
    "storage/app.db"
  )
  for p in "${CANDIDATES[@]}"; do
    if [[ -f "$p" ]]; then
      DB_PATH="$p"
      break
    fi
  done
fi

if [[ -z "${DB_PATH}" ]]; then
  # last resort: search
  DB_PATH="$(find . -maxdepth 4 -type f -name '*.db' | head -n1 || true)"
fi

if [[ -z "${DB_PATH}" || ! -f "${DB_PATH}" ]]; then
  echo "ERROR: SQLite DB file not found. Set DB_PATH env or place DB under repo."
  exit 1
fi

echo "DB_PATH=${DB_PATH}"

# ----- target path (/tmp is writable on Render) -----
TS="$(date -u +'%Y%m%dT%H%M%SZ')"
OUT_DIR="/tmp/backups"
OUT_RAW="${OUT_DIR}/sqlite_${TS}.db"
OUT_GZ="${OUT_RAW}.gz"

mkdir -p "${OUT_DIR}"

# ----- make a consistent backup via sqlite3 .backup -----
if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "ERROR: sqlite3 is not installed in this image."
  exit 1
fi

echo "Creating backup to ${OUT_RAW}"
sqlite3 "${DB_PATH}" ".backup '${OUT_RAW}'"

# ----- compress -----
echo "Compressing ${OUT_RAW} -> ${OUT_GZ}"
gzip -f "${OUT_RAW}"

# ----- optional S3 upload -----
# Requires: awscli available and env S3_BUCKET set (e.g. s3://my-bucket/elaya/)
if [[ -n "${S3_BUCKET:-}" ]]; then
  if command -v aws >/dev/null 2>&1; then
    S3_KEY_PREFIX="${S3_KEY_PREFIX:-backups}"
    S3_URI="${S3_BUCKET%/}/${S3_KEY_PREFIX}/$(basename "${OUT_GZ}")"
    echo "Uploading to ${S3_URI}"
    aws s3 cp "${OUT_GZ}" "${S3_URI}" --only-show-errors
    echo "Uploaded to S3."
  else
    echo "WARN: S3_BUCKET set but awscli not found. Skipping upload."
  fi
else
  echo "S3 upload disabled (S3_BUCKET not set)."
fi

# ----- list result -----
ls -lh "${OUT_GZ}" || true
echo "==> Backup completed successfully."
