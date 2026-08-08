---
bug_id: BUG-2026-08-07T0118-plan-consistency-gates
status: open
severity: low
scope: planning-infrastructure
title: Required plan consistency and status-sync gate scripts are absent
---

# BUG-2026-08-07T0118: Required lifecycle gates are absent

## Problem

The project conventions require runnable planning, verification, and audit gates. The installed `plan-work`, `change-request`, `verify-work`, and `audit-code` workflows require `scripts/lib/plan-consistency-check.sh`, `scripts/sync-status-from-epics.sh`, `scripts/check-blind-spots.sh`, `scripts/lib/completeness-critic.sh`, and `scripts/bp-churn-rank.sh`, but none exists in this repository.

Expected behavior: the documented lifecycle gates run and produce deterministic results.

Actual behavior: all five commands exit non-zero because their script paths do not exist.

## Reproduction

1. Run `bash scripts/lib/plan-consistency-check.sh specs/epics/e08-npm-dependency-maturity/`.
2. Observe `No such file or directory`.
3. Run `bash scripts/sync-status-from-epics.sh`.
4. Run `bash scripts/check-blind-spots.sh`.
5. Run `bash scripts/lib/completeness-critic.sh`.
6. Run `bash scripts/bp-churn-rank.sh --since 90.days --limit 15`.
7. Observe `No such file or directory` for each missing script.

## Impact

Security impact: NONE. The missing scripts do not alter runtime dependency acquisition. They prevent the prescribed automated consistency and status-sync checks from proving planning artifacts are aligned.

## Required follow-up

Create a separately scoped and planned lifecycle-infrastructure story that implements all five scripts and tests their behavior. Do not represent the missing gates as passed; use explicit manual cross-artifact verification and record unavailable checks as `not_run` until that story is delivered.
