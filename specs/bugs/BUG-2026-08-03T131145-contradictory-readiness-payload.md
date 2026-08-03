---
bug_id: BUG-2026-08-03T131145-contradictory-readiness-payload
status: fixed
severity: medium
scope: reviewer-readiness
security_impact: none
title: Contradictory readiness payload can display overall ready
---

# BUG-2026-08-03T131145: Contradictory readiness payload can display overall ready

## Problem

The reviewer interface accepts a successful readiness payload whose overall state is `ready` even when a dependency state is `unavailable`.

Expected behavior: the browser trust-boundary parser must reject every internally contradictory response and fall back to API unavailable with dependencies not checked.

Actual behavior: the parser checks HTTP-to-overall status agreement and validates individual enum values, but it does not check their relationship. An HTTP 200 response with overall `ready`, database `unavailable`, and pgvector `not_checked` displays overall ready.

Reproduction:

1. Pass HTTP status 200 and a structurally valid payload with overall `ready` and an unavailable dependency to the public readiness interpreter.
2. Observe `api=ready` and `overall=ready` in the returned view.
3. Observe that the same view also contains the unavailable dependency.

Security impact: NONE. No security exploit path was identified. The defect concerns truthful local reviewer status.

This defect is novel and does not share a root cause with the database lifecycle issues.

## Root Cause Analysis

### Reproduce

The public readiness interpreter returned `api=ready`, `overall=ready`, `database=unavailable`, and `pgvector=not_checked` for a contradictory HTTP 200 payload.

### Isolate

The browser fetch and rendering layers preserved the interpreter result. The issue is isolated to response semantic validation, after shape and enum validation but before the display view is created.

### Hypothesize

1. **Missing cross-field invariant:** The parser validates fields independently and never requires ready dependencies for overall ready. Falsification: inspect and exercise the semantic predicate with contradictory valid enum values.
2. **HTTP status ignored:** The parser accepts the response because it does not validate status 200 versus 503. Falsification: pass an unsupported status or an HTTP-to-overall mismatch.
3. **Rendering overwrites the state:** The parser returns unavailable, but the component converts it to ready. Falsification: inspect the direct interpreter result before rendering.

### Verify

Unsupported HTTP status and HTTP-to-overall mismatch already fall back to unavailable. The direct interpreter result remains contradictory before rendering. The semantic predicate checks no dependency relationship.

Confirmed root cause: readiness validation enforces field types and HTTP status but omits the cross-field dependency invariant.

Risk level: Medium. False overall readiness undermines the reviewer workspace's fail-closed status contract.

## TDD Fix Plan

1. **RED:** Add contradictory HTTP 200 and HTTP 503 payloads to the public interpreter contract and require the bounded unavailable fallback.
   **GREEN:** Add one semantic predicate that accepts only the backend's coherent ready, database-unavailable, and pgvector-unavailable combinations.
   **verify:** `npm run test:unit`

**REFACTOR:** Keep shape, enum, HTTP, and cross-field validation as named predicates without changing the display model.

## Acceptance Criteria

- [x] Overall ready is accepted only when the database and pgvector are both ready.
- [x] Database unavailable is accepted only with pgvector not checked and overall unavailable.
- [x] pgvector unavailable is accepted only with the database ready and overall unavailable.
- [x] Contradictory payloads use the bounded API-unavailable fallback.
- [x] The regression test passes.
- [x] `make preflight` passes.

## Resolution

**Fixed:** 2026-08-03

**Root cause confirmed:** The parser validated field types and HTTP agreement but omitted the dependency-state relationship.

**Fix applied:** One semantic predicate now accepts only the backend's coherent healthy, database-unavailable, and pgvector-unavailable combinations.

**Hardening added:** Every other shape-valid combination uses the bounded API-unavailable fallback. The generalization sweep found no second explicit payload parser without cross-field validation.

**Evidence:** The unit regression and behavioral interpreter proof passed, all 15 Python tests, one Node test, and five Playwright tests passed, TypeScript and lint passed, `npm audit` reported zero vulnerabilities, and `make preflight` passed.

**Commit:** `68db9f6` — `fix(web): enforce readiness state coherence`
