---
bug_id: BUG-2026-08-03T131144-failed-database-start-cleanup
status: fixed
severity: medium
scope: local-database
security_impact: low
title: Failed database startup leaves the container running
---

# BUG-2026-08-03T131144: Failed database startup leaves the container running

## Problem

A database startup failure that occurs after container creation returns a nonzero status but leaves the project container running.

Expected behavior: startup is atomic from the operator's perspective. A failed start must stop the container that the attempt created or replaced.

Actual behavior: credential, health, or extension validation can fail after the container starts. The command exits without running the stop path, so the loopback listener and container remain active.

Reproduction:

1. Create a mode `0700` runtime directory with syntactically valid environment files that contain an invalid generated credential.
2. Start the local database on an available loopback port.
3. Observe a nonzero startup status.
4. Inspect the project container and observe that it is still running.

Security impact: LOW. The orphaned service remains loopback-only and no exploit path was identified, but stale local services and resources outlive a failed operation.

This issue is related to the fresh-runtime credential defect because that fix added an earlier post-start validation failure. Its root cause is separate: startup has no rollback boundary.

## Root Cause Analysis

### Reproduce

The audit started the database with invalid generated credential configuration on loopback port 55436. Startup exited with status 1, while the project container state remained `running`.

### Isolate

The failure occurred after the rootless container reached healthy state and before readiness output. Manual stop succeeded. The command log contained no automatic stop operation, which isolates the problem to database lifecycle rollback rather than Podman stop behavior.

### Hypothesize

1. **Missing post-create rollback:** The startup path has no exit cleanup after container creation. Falsification: inspect whether any failed post-create command invokes the stop path.
2. **Podman stop failure:** Cleanup ran but Podman could not stop the container. Falsification: inspect the command log and run the same stop path manually.
3. **External container ownership:** The running container was not created by the failed start. Falsification: verify that startup used the fixed project name with replacement and the selected port.

### Verify

No stop operation followed the failing validation. The same public stop command then exited successfully and changed the container to `exited`. Startup used the fixed project container name and requested port.

Confirmed root cause: the database lifecycle clears no partial start because it installs no cleanup guard after successful container creation.

Risk level: Medium. Failed startup can leak a local listener and cause later port, credential, or state confusion.

## TDD Fix Plan

1. **RED:** Add a database lifecycle contract where a post-create validation failure returns nonzero and verify that the public start command stops the created container.
   **GREEN:** Install a failed-start cleanup guard immediately after successful container creation, preserve the original failure status, and clear the guard only after all readiness checks pass.
   **verify:** `uv run --locked python -m unittest tests.contract.test_database_container.DatabaseContainerContractTests.test_failed_start_stops_created_container`

**REFACTOR:** Keep successful stop behavior and failed-start rollback on one container-stop operation.

## Acceptance Criteria

- [x] A post-create startup failure returns nonzero.
- [x] The failed attempt stops the project container.
- [x] The original failure remains visible and is not replaced by cleanup output.
- [x] Successful startup still leaves the container running until an explicit stop.
- [x] The regression test passes.
- [x] `make preflight` passes.

## Resolution

**Fixed:** 2026-08-03

**Root cause confirmed:** The lifecycle installed no cleanup guard after container creation, so later validation exits bypassed the stop operation.

**Fix applied:** Startup now installs an exit rollback immediately after successful container creation and clears it only after all readiness checks pass.

**Hardening added:** The guard preserves the original status, uses the existing volume-preserving stop operation, and covers every post-create failure. The generalization sweep found no second persistent resource start.

**Evidence:** The targeted regression passed, all 15 Python tests, one Node test, and five Playwright tests passed, TypeScript and lint passed, and `make preflight` passed. Live invalid-configuration validation returned status 1 and left the project container exited.

**Commit:** `327ca4b` — `fix(database): clean up failed startup`
