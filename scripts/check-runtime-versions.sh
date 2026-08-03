#!/usr/bin/env bash
# story: e01s01
set -euo pipefail

REQUIRED_PYTHON="3.14.6"
REQUIRED_NODE="24.18.1"
REQUIRED_NPM="11.16.0"
MINIMUM_PODMAN="5.7.0"

require_exact_version() {
  local label=$1 required=$2 detected=$3
  [[ "$detected" == "$required" ]] && return
  echo "$label version mismatch: required $required, detected $detected" >&2
  exit 1
}

require_minimum_version() {
  local label=$1 required=$2 detected=$3 minimum
  minimum=$(printf '%s\n%s\n' "$required" "$detected" | sort -V | head -n 1)
  [[ "$minimum" == "$required" ]] && return
  echo "$label version mismatch: required at least $required, detected $detected" >&2
  exit 1
}

for tool in uv node npm podman; do
  command -v "$tool" >/dev/null || {
    echo "Missing required tool: $tool" >&2
    exit 1
  }
done

python_version=$(uv run --locked python --version | awk '{print $2}')
node_version=$(node --version | sed 's/^v//')
npm_version=$(npm --version)
podman_version=$(podman version --format '{{.Client.Version}}')
podman_rootless=$(podman info --format '{{.Host.Security.Rootless}}')

require_exact_version "Python" "$REQUIRED_PYTHON" "$python_version"
require_exact_version "Node.js" "$REQUIRED_NODE" "$node_version"
require_exact_version "npm" "$REQUIRED_NPM" "$npm_version"
require_minimum_version "Podman" "$MINIMUM_PODMAN" "$podman_version"

if [[ "$podman_rootless" != "true" ]]; then
  echo "Podman must run rootless: detected $podman_rootless" >&2
  exit 1
fi

echo "Runtime contract OK: Python $python_version, Node.js $node_version, npm $npm_version, rootless Podman $podman_version"
