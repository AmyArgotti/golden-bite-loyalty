#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
APP_ENV_EXPECTED="${APP_ENV_EXPECTED:-production}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Environment file not found: $ENV_FILE"
  exit 1
fi

set -a
. "$ENV_FILE"
set +a

require_var() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "Missing required env var: $name"
    exit 1
  fi
}

echo "Validating environment file: $ENV_FILE"

require_var APP_ENV
require_var SECRET_KEY
require_var POSTGRES_USER
require_var POSTGRES_PASSWORD
require_var POSTGRES_DB
require_var DATABASE_URL
require_var REDIS_URL
require_var SMS_PROVIDER
require_var WALLET_PASSES_DIR
require_var LOYALTY_RULES_PATH

if [[ "$APP_ENV" != "$APP_ENV_EXPECTED" ]]; then
  echo "APP_ENV should be '$APP_ENV_EXPECTED' but is '$APP_ENV'"
  exit 1
fi

if [[ "$DATABASE_URL" != *"$POSTGRES_USER"* ]] || [[ "$DATABASE_URL" != *"$POSTGRES_PASSWORD"* ]] || [[ "$DATABASE_URL" != *"$POSTGRES_DB"* ]]; then
  echo "DATABASE_URL does not appear to match POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB"
  exit 1
fi

case "$SMS_PROVIDER" in
  sms_ru)
    require_var SMS_RU_API_ID
    ;;
  twilio)
    require_var TWILIO_ACCOUNT_SID
    require_var TWILIO_AUTH_TOKEN
    require_var TWILIO_FROM_NUMBER
    ;;
  generic_http)
    require_var SMS_API_URL
    require_var SMS_API_KEY
    ;;
  mock)
    echo "Warning: SMS_PROVIDER=mock is not production-safe"
    ;;
  *)
    echo "Unsupported SMS_PROVIDER: $SMS_PROVIDER"
    exit 1
    ;;
esac

if [[ -n "${WALLET_WEB_SERVICE_URL:-}" ]]; then
  require_var WALLET_PASS_TYPE_IDENTIFIER
  require_var WALLET_TEAM_IDENTIFIER
fi

if [[ "$APP_ENV_EXPECTED" == "production" ]]; then
  require_var WALLET_SIGNING_CERT_PATH
  require_var WALLET_SIGNING_KEY_PATH
  require_var WALLET_WWDR_CERT_PATH
fi

echo "Environment validation passed."
