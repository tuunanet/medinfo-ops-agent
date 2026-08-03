#!/usr/bin/env bash
# story: e01s01
set -euo pipefail

REPOSITORY_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
RUNTIME_DIR=${MEDINFO_RUNTIME_DIR:-"$REPOSITORY_ROOT/.tmp/database"}
CONTAINER_ENV="$RUNTIME_DIR/postgres.env"
APPLICATION_ENV="$RUNTIME_DIR/application.env"
CONTAINER_NAME="medinfo-ops-postgres"
VOLUME_NAME="medinfo-ops-postgres-data"
IMAGE="docker.io/pgvector/pgvector:0.8.6-pg18-trixie"
DATABASE_PORT=${DATABASE_PORT:-5432}

ensure_runtime_config() {
  mkdir -p "$RUNTIME_DIR"
  chmod 700 "$RUNTIME_DIR"
  [[ -f "$CONTAINER_ENV" && -f "$APPLICATION_ENV" ]] && return

  local password
  password=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
  umask 077
  printf 'POSTGRES_DB=medinfo\nPOSTGRES_USER=medinfo\nPOSTGRES_PASSWORD=%s\n' \
    "$password" > "$CONTAINER_ENV"
  printf 'DATABASE_URL=postgresql://medinfo:%s@127.0.0.1:%s/medinfo\n' \
    "$password" "$DATABASE_PORT" > "$APPLICATION_ENV"
  chmod 600 "$CONTAINER_ENV" "$APPLICATION_ENV"
}

cleanup_failed_start() {
  local status=$?
  trap - EXIT
  stop_database || \
    echo "Warning: database cleanup after failed start did not complete" >&2
  exit "$status"
}

read_database_password() {
  local config_lines=() password
  mapfile -t config_lines < "$CONTAINER_ENV"
  if ((${#config_lines[@]} != 3)) || \
    [[ "${config_lines[0]}" != POSTGRES_DB=medinfo ]] || \
    [[ "${config_lines[1]}" != POSTGRES_USER=medinfo ]] || \
    [[ "${config_lines[2]}" != POSTGRES_PASSWORD=* ]]; then
    echo "Database container configuration is invalid" >&2
    exit 1
  fi
  password=${config_lines[2]#POSTGRES_PASSWORD=}
  if [[ ! "$password" =~ ^[A-Za-z0-9_-]{43}$ ]]; then
    echo "Database container configuration is invalid" >&2
    exit 1
  fi
  printf '%s' "$password"
}

wait_until_healthy() {
  local attempt health
  for attempt in $(seq 1 30); do
    health=$(podman inspect --format '{{.State.Health.Status}}' \
      "$CONTAINER_NAME" 2>/dev/null || true)
    [[ "$health" == "healthy" ]] && return
    sleep 1
  done
  echo "PostgreSQL container did not become healthy within 30 seconds" >&2
  exit 1
}

synchronize_database_password() {
  local password
  password=$(read_database_password)
  printf "ALTER ROLE medinfo PASSWORD '%s';\n" "$password" | \
    podman exec --interactive "$CONTAINER_NAME" psql \
      --no-psqlrc --quiet --set ON_ERROR_STOP=1 \
      --username medinfo --dbname medinfo >/dev/null
}

create_vector_extension() {
  local vector_version
  vector_version=$(podman exec "$CONTAINER_NAME" psql \
    --no-psqlrc --tuples-only --no-align \
    --username medinfo --dbname medinfo \
    --command "CREATE EXTENSION IF NOT EXISTS vector; SELECT extversion FROM pg_extension WHERE extname = 'vector';" \
    | tail -n 1)
  if [[ "$vector_version" != "0.8.6" ]]; then
    echo "pgvector version mismatch: required 0.8.6, detected $vector_version" >&2
    exit 1
  fi
}

start_database() {
  ensure_runtime_config
  podman volume exists "$VOLUME_NAME" || podman volume create "$VOLUME_NAME" >/dev/null
  podman run --detach --replace \
    --name "$CONTAINER_NAME" \
    --publish "127.0.0.1:${DATABASE_PORT}:5432" \
    --env-file "$CONTAINER_ENV" \
    --volume "$VOLUME_NAME:/var/lib/postgresql" \
    --health-cmd "pg_isready --username medinfo --dbname medinfo" \
    --health-interval 1s --health-retries 30 \
    "$IMAGE" >/dev/null
  trap cleanup_failed_start EXIT
  wait_until_healthy
  synchronize_database_password
  create_vector_extension
  trap - EXIT
  echo "PostgreSQL 18 with pgvector 0.8.6 is ready on 127.0.0.1:$DATABASE_PORT"
}

stop_database() {
  if podman container exists "$CONTAINER_NAME"; then
    podman stop --time 5 "$CONTAINER_NAME" >/dev/null
  fi
}

show_status() {
  podman inspect --format '{{.State.Status}}' "$CONTAINER_NAME"
}

case "${1:-}" in
  start) start_database ;;
  stop) stop_database ;;
  status) show_status ;;
  *) echo "Usage: $0 {start|stop|status}" >&2; exit 2 ;;
esac
