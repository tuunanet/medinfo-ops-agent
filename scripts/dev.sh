#!/usr/bin/env bash
# story: e01s01
set -euo pipefail

REPOSITORY_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
RUNTIME_DIR=${MEDINFO_RUNTIME_DIR:-"$REPOSITORY_ROOT/.tmp/database"}
APPLICATION_ENV="$RUNTIME_DIR/application.env"
API_PORT=${API_PORT:-8000}
WEB_PORT=${WEB_PORT:-3000}
HOST_PROCESSES=()
DATABASE_STARTED=false

require_port() {
  local label=$1 port=$2
  if [[ ! "$port" =~ ^[0-9]+$ ]] || ((port < 1 || port > 65535)); then
    echo "$label must be an integer from 1 through 65535: detected $port" >&2
    exit 1
  fi
}

load_database_url() {
  local config_lines=()
  [[ -r "$APPLICATION_ENV" ]] || {
    echo "Database application configuration is unavailable" >&2
    exit 1
  }
  mapfile -t config_lines < "$APPLICATION_ENV"
  if ((${#config_lines[@]} != 1)) || [[ "${config_lines[0]}" != DATABASE_URL=* ]]; then
    echo "Database application configuration is invalid" >&2
    exit 1
  fi
  DATABASE_URL=${config_lines[0]#DATABASE_URL=}
  [[ -n "$DATABASE_URL" ]] || {
    echo "Database application configuration is invalid" >&2
    exit 1
  }
  export DATABASE_URL
}

stop_workspace() {
  local status=$?
  trap - EXIT INT TERM

  local process_id
  for process_id in "${HOST_PROCESSES[@]}"; do
    # e01s01 owns descendants that uv and npm create for each host process.
    kill -TERM -- "-$process_id" 2>/dev/null || true
  done
  for process_id in "${HOST_PROCESSES[@]}"; do
    wait "$process_id" 2>/dev/null || true
  done
  if [[ "$DATABASE_STARTED" == true ]]; then
    "$REPOSITORY_ROOT/scripts/database-container.sh" stop || \
      echo "Warning: PostgreSQL container cleanup failed" >&2
  fi
  exit "$status"
}

wait_for_host_exit() {
  local status
  set +e
  wait -n "${HOST_PROCESSES[@]}"
  status=$?
  set -e
  if ((status != 0)); then
    echo "Host process exited with status $status" >&2
  fi
  return "$status"
}

trap stop_workspace EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

require_port "API_PORT" "$API_PORT"
require_port "WEB_PORT" "$WEB_PORT"
command -v setsid >/dev/null || {
  echo "Missing required tool: setsid" >&2
  exit 1
}
"$REPOSITORY_ROOT/scripts/check-runtime-versions.sh"
"$REPOSITORY_ROOT/scripts/database-container.sh" start
DATABASE_STARTED=true
load_database_url

setsid uv run --locked uvicorn services.api.medinfo_api.main:app \
  --host 127.0.0.1 --port "$API_PORT" &
HOST_PROCESSES+=("$!")
API_BASE_URL="http://127.0.0.1:$API_PORT" \
  setsid npm run dev --workspace @medinfo/web -- \
  --hostname 127.0.0.1 --port "$WEB_PORT" &
HOST_PROCESSES+=("$!")

echo "Reviewer workspace starting on http://127.0.0.1:$WEB_PORT"
echo "FastAPI starting on http://127.0.0.1:$API_PORT"
wait_for_host_exit
