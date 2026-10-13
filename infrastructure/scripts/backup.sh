#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/backups}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
mkdir -p "$BACKUP_DIR"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is required"
  exit 1
fi

BACKUP_PATH="$BACKUP_DIR/golden_bite_${TIMESTAMP}.sql.gz"
pg_dump "$DATABASE_URL" | gzip > "$BACKUP_PATH"
find "$BACKUP_DIR" -type f -name 'golden_bite_*.sql.gz' -mtime +"$RETENTION_DAYS" -delete
echo "Backup written to $BACKUP_PATH"
