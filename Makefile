# story: e01s01
SHELL := /usr/bin/env bash
.DEFAULT_GOAL := test

.PHONY: dev test build lint preflight

dev:
	@scripts/dev.sh

test:
	@uv run --locked python -m unittest discover -s tests -p 'test_*.py'
	@npm test

build:
	@scripts/run-build.sh

lint:
	@scripts/run-lint.sh

preflight:
	@scripts/run-preflight.sh
