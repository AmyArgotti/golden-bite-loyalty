#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/infrastructure/docker/docker-compose.prod.yml"
BACKEND_SERVICE="${BACKEND_SERVICE:-backend}"
POSTGRES_SERVICE="${POSTGRES_SERVICE:-postgres}"

echo "Deploying Golden Bite Loyalty from $ROOT_DIR"
docker compose -f "$COMPOSE_FILE" pull || true
docker compose -f "$COMPOSE_FILE" build
docker compose -f "$COMPOSE_FILE" up -d

echo "Waiting for PostgreSQL..."
for _ in $(seq 1 30); do
  if docker compose -f "$COMPOSE_FILE" exec -T "$POSTGRES_SERVICE" pg_isready -U "${POSTGRES_USER:-golden_bite}" > /dev/null 2>&1; then
    echo "PostgreSQL is ready"
    break
  fi
  sleep 2
done

docker compose -f "$COMPOSE_FILE" exec -T "$BACKEND_SERVICE" sh -lc "PYTHONPATH=. alembic upgrade head"
echo "Waiting for API health..."
for _ in $(seq 1 30); do
  if docker compose -f "$COMPOSE_FILE" exec -T "$BACKEND_SERVICE" python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health', timeout=5)"; then
    echo "API is healthy"
    exit 0
  fi
  sleep 2
done
echo "API health check did not pass in time"
exit 1
