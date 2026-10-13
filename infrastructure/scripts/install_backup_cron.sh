#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
CRON_SCHEDULE="${CRON_SCHEDULE:-0 3 * * *}"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
BACKUP_SCRIPT="$ROOT_DIR/infrastructure/scripts/backup.sh"
LOG_FILE="${LOG_FILE:-$ROOT_DIR/backups/backup.log}"

mkdir -p "$(dirname "$LOG_FILE")"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Environment file not found: $ENV_FILE"
  exit 1
fi

CRON_ENTRY="$CRON_SCHEDULE cd $ROOT_DIR && set -a && . $ENV_FILE && set +a && $BACKUP_SCRIPT >> $LOG_FILE 2>&1"

(
  crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT" || true
  echo "$CRON_ENTRY"
) | crontab -

echo "Installed backup cron:"
echo "$CRON_ENTRY"
