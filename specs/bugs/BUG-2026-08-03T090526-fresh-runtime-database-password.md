---
bug_id: BUG-2026-08-03T090526-fresh-runtime-database-password
status: fixed
severity: medium
scope: local-database
security_impact: low
title: Fresh runtime credentials do not match preserved PostgreSQL data
---

# BUG-2026-08-03T090526: Fresh runtime credentials do not match preserved PostgreSQL data

## Problem

Starting the local database with a fresh runtime directory can report that PostgreSQL and pgvector are ready while the API cannot authenticate to the preserved database volume.

Expected behavior: every successful database start publishes application credentials that can connect to the preserved local database, including after the operator changes the database port and runtime directory.

Actual behavior: a fresh runtime directory generates a new password. PostgreSQL applies its bootstrap password only when it initializes an empty data directory, so a preserved volume retains the previous role password. Container health and local extension checks still pass, but API readiness reports the database as unavailable.

Reproduction:

1. Start the local database once so that the named data volume is initialized.
2. Stop it.
3. Start it on another available loopback port with a fresh `MEDINFO_RUNTIME_DIR`.
4. Observe that the database script reports ready.
5. Probe readiness with the generated `DATABASE_URL` and observe `database=unavailable` and `pgvector=not_checked`.

Security impact: LOW. No security exploit path was identified. The mismatch causes local unavailability; it does not expose credentials or protected data.

This defect is novel. The earlier cleanup-marker bug affected test signal timing and has a different root cause.

## Root Cause Analysis

### Reproduce

The audit started the preserved named volume on loopback port 55433 with a new runtime directory. The database script reported PostgreSQL 18 and pgvector 0.8.6 ready, but the application readiness probe returned `database=unavailable` and `pgvector=not_checked`.

### Isolate

The container health check passed, local SQL access succeeded, the vector extension version was correct, and the generated application URL used the requested port. The failure was isolated to password authentication between the generated application configuration and the existing database role.

### Hypothesize

1. **Bootstrap-only password configuration:** PostgreSQL ignores a new container password when the data volume is already initialized. Falsification: synchronize the existing role password to the newly generated credential and retry the same application probe.
2. **Stale port configuration:** The generated application URL retained an earlier port. Falsification: inspect only the URL port and compare it with the published loopback port.
3. **Database or extension startup failure:** The readiness probe failed because PostgreSQL or pgvector was not ready. Falsification: run local SQL and inspect the extension version before changing credentials.
4. **Client incompatibility:** The application client could not connect to PostgreSQL 18. Falsification: retry the same client and URL after changing only the role password.

### Verify

The generated URL used the requested port, local SQL access succeeded, and pgvector reported version 0.8.6. Before password synchronization, the application probe reported the database unavailable. After synchronizing only the existing role password to the generated credential through local container SQL, the same probe reported both the database and pgvector ready.

Confirmed root cause: runtime credential generation assumes that the container password reconfigures an already initialized PostgreSQL role, but that environment variable is bootstrap-only.

Risk level: Medium. The defect blocks local startup whenever a fresh runtime configuration is paired with the preserved named volume.

## TDD Fix Plan

1. **RED:** Extend the public database lifecycle contract to start the same preserved fake database through two fresh runtime directories and verify that each published application credential matches the database role after startup.
   **GREEN:** During startup, validate the generated credential and synchronize the local development role through container-local SQL before reporting readiness. Keep the credential out of command arguments and logs.
   **verify:** `uv run --locked python -m unittest tests.contract.test_database_container.DatabaseContainerContractTests.test_fresh_runtime_credentials_match_preserved_database`

**REFACTOR:** Keep database initialization, credential validation, role synchronization, and extension validation as named lifecycle responsibilities.

## Acceptance Criteria

- [x] A second fresh runtime directory can use the preserved named database volume.
- [x] The application credential matches the database role before startup reports ready.
- [x] Credentials do not appear in process arguments, command logs, or successful test output.
- [x] Generated runtime files remain mode `0600` in a mode `0700` directory.
- [x] The regression test passes.
- [x] `make preflight` passes.
- [x] Manual readiness reports the database and pgvector ready after a fresh-runtime restart.

## Resolution

**Fixed:** 2026-08-03

**Root cause confirmed:** PostgreSQL uses the container password only during data initialization, while each fresh runtime directory generated a new application credential.

**Fix applied:** Startup now validates the generated credential and synchronizes the fictional local role through container standard input before extension validation and readiness output.

**Hardening added:** Strict credential shape validation blocks SQL metacharacters, the regression checks preserved-volume behavior and command-log secrecy, and the generalization sweep found no second persistent-service credential boundary.

**Evidence:** The targeted regression passed, all 14 Python tests, one Node test, and five Playwright tests passed, TypeScript and lint passed, `npm audit` reported zero vulnerabilities, and `make preflight` passed. Live validation on loopback port 55435 reported both the database and pgvector ready and retained `0700` and `0600` permissions.

**Commit:** `0b76cb8` — `fix(database): synchronize fresh runtime credentials`
