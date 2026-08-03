#!/usr/bin/env bash
# story: e01s01
set -euo pipefail

REPOSITORY_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$REPOSITORY_ROOT"

unset OPENAI_API_KEY AZURE_OPENAI_API_KEY
export MEDINFO_ALLOW_PAID_PROVIDER_CALLS=false

scripts/check-runtime-versions.sh
uv lock --check
npm ci --ignore-scripts --dry-run --no-audit --no-fund
make lint
make test
make build

echo "Preflight complete: runtime, locks, lint, tests, and build passed"
