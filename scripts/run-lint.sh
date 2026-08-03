#!/usr/bin/env bash
# story: e01s01
set -euo pipefail

REPOSITORY_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$REPOSITORY_ROOT"

uv run --locked ruff check .
uv run --locked ruff format --check .
npm run lint
