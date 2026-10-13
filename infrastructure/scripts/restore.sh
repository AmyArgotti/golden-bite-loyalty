#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: restore.sh <backup-file.sql>"
  exit 1
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is required"
  exit 1
fi

if [[ "$1" == *.gz ]]; then
  gunzip -c "$1" | psql "$DATABASE_URL"
else
  psql "$DATABASE_URL" < "$1"
fi

echo "Restore complete"
