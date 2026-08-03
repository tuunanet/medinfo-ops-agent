---
bug_id: BUG-2026-08-03T0841-flaky-cleanup-marker
status: fixed
severity: medium
scope: test-infrastructure
title: Cleanup test marker races with signal setup
---

# BUG-2026-08-03T0841: Cleanup test marker races with signal setup

## Problem

The development-orchestration cleanup test can fail even when the production orchestrator terminates every process group correctly. The fake web process sometimes exits without writing its termination evidence.

Expected behavior: a fake host-process start marker means that the process is ready to receive and record a termination signal.

Actual behavior: the marker can become visible before the termination trap exists. A signal in that interval exits the fake process without the expected log entry.

Reproduction:

1. Run `make test` repeatedly or as part of the `verify-work` mechanical gate.
2. Observe an intermittent cleanup-test failure because the npm termination entry is absent.
3. Confirm that the API descendant and database cleanup evidence still exists.

Security impact: NONE. No security exploit path was identified. The defect affects deterministic verification only.

## Root Cause Analysis

### Reproduce

The `verify-work` mechanical test run failed with one cleanup-test assertion. Twelve Python tests had completed except for the missing fake npm termination evidence. Earlier runs of the same suite passed.

### Isolate

The failure is isolated to signal-readiness semantics in the development-orchestration test fixture. Production cold-start shutdown completed with PostgreSQL exit code 0, no OOM kill, closed ports, and no remaining host processes.

### Hypothesize

1. **Marker-before-trap race:** the fake process publishes readiness before installing its termination trap. Falsification: add a bounded delay in that interval and terminate immediately after the marker.
2. **Production process-group cleanup failure:** the orchestrator does not signal the fake web process. Falsification: inspect production and manual shutdown evidence for leaked processes.
3. **Concurrent log-write loss:** multiple fake processes overwrite evidence. Falsification: confirm every writer opens the command log in append mode.

### Verify

A temporary signal harness reproduced the race deterministically: marker-before-trap produced no termination entry, while trap-before-marker produced the entry under the same signal timing. Production shutdown evidence falsified hypothesis 2, and append-only writes falsified hypothesis 3.

Confirmed root cause: the test fixture publishes a start marker before its signal handler is ready.

Risk level: Low. The defect can create false-negative verification results but does not change product behavior.

## TDD Fix Plan

1. **RED:** Add a bounded post-marker delay to the cleanup scenario so termination deterministically reaches the existing marker-before-trap interval.
   **GREEN:** Install each fake host process termination trap before publishing its start marker.
   **verify:** `uv run --locked python -m unittest tests.contract.test_development_orchestration.DevelopmentOrchestrationContractTests.test_termination_stops_descendant_processes_and_database`

**REFACTOR:** Keep marker semantics consistent across the fake API worker, API parent, and web process.

## Acceptance Criteria

- [x] A start marker is emitted only after the corresponding termination trap exists.
- [x] The deterministic race regression test passes.
- [x] Repeated cleanup-test runs pass.
- [x] `make preflight` passes.
- [x] Existing manual shutdown evidence remains valid.

## Resolution

**Fixed:** 2026-08-03

**Root cause confirmed:** The shell test fixtures published start markers before their termination traps were ready.

**Fix applied:** The fake API parent, API worker, and npm process now install termination traps before publishing readiness markers.

**Hardening added:** A bounded signal-setup delay makes the former race deterministic. The generalization sweep found zero remaining marker-before-handler instances under `tests/`.

**Evidence:** The regression passed 25 consecutive runs, the full suite passed, TypeScript type checking passed, lint passed, and `make preflight` passed.

**Commit:** `97b5cbd` — `fix(test): publish cleanup markers after signal setup`
