#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1}"

check_url() {
  local label="$1"
  local url="$2"
  echo "Checking $label -> $url"
  curl --fail --silent --show-error --location "$url" > /dev/null
}

check_url "api health" "$BASE_URL/api/v1/health"
check_url "customer app" "$BASE_URL/"
check_url "staff panel" "$BASE_URL/staff"
check_url "admin panel" "$BASE_URL/admin"

echo "Smoke checks passed."
