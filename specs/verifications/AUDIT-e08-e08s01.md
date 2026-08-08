# Audit: e08s01 — Npm Dependency Maturity and Acquisition Controls

- Audited: 2026-08-07
- Scope: `origin/main...fd55d9e`
- Verdict: PASS for the implementation diff

## Supply chain and security

- [x] No new package was added. The plan tags the existing npm 11.16.0 toolchain `[OK]`.
- [x] Direct dependency ranges were narrowed to the existing lockfile versions; version comparison found zero resolved package-version changes.
- [x] The diff secret-pattern scan found no token, AWS key, or private-key pattern.
- [x] The project policy fixes an HTTPS registry, enables the 30-day maturity hold, disables dependency lifecycle scripts, and denies directory, file, git, and remote sources.
- [x] `specs/security/REVIEW.md` records no unresolved HIGH finding at confidence 8/10 or higher.

## Provenance and scope

- [x] The story records `TYPE: feat`, `CONTEXT: infrastructure`, the threat model, prior art, ADR-0003, and runnable P0 verification tasks.
- [x] Changes are limited to npm acquisition policy, exact direct specifications, contract coverage, Preflight enforcement, decision records, and verification evidence.
- [x] The absent lifecycle helper scripts were logged as `BUG-2026-08-07T0118-plan-consistency-gates`; they are recorded as `not_run`, not passed.

## Correctness, types, and tests

- [x] Policy tests exercise the public project configuration, lockfile, and Preflight command contract without registry network access.
- [x] New Python helpers have explicit types; no TypeScript `any`, suppression, or unsafe cast was added.
- [x] The new test module is 105 lines; its helpers separate configuration, lockfile-source, and direct-version assertions.
- [x] No dead code, commented-out code, message chain, injection sink, auth change, or untrusted deserialization was added.
- [x] The final `make preflight` terminal verdict is recorded in `specs/verifications/e08s01-verify.yaml`.

## Red-flag check

No checklist item was skipped as passed. The churn, plan-consistency, status-sync, blind-spot, and completeness helper scripts are absent in the project baseline; the open lifecycle-infrastructure bug records each unavailable check.

---

## Review-correction audit

- Audited: 2026-08-07
- Scope: `66ccbb6...4b0cf82`
- Verdict: PASS

- [x] The standard-library source-policy CLI is 175 lines, has one responsibility, invokes no shell or network operation, and fails closed for malformed or unapproved project files.
- [x] It validates project npm controls, scoped registry overrides, every declared workspace manifest, registry-only lock entries, SHA-512 integrity, and the only allowed workspace link.
- [x] The tests use public CLI behavior: real npm 11.16.0 rejects a temporary directory dependency; temporary manifest/lockfile fixtures reject directory, tarball-file, git, shorthand-git, remote, and scoped-registry sources.
- [x] The code contains no secret, dynamic evaluation, unsafe deserialization, TypeScript suppression, new dependency, or GitHub API path.
- [x] Preflight runs the fixed source-policy CLI before its frozen npm command; `make preflight` passed with 22 Python tests, one Node test, five Playwright tests, lint, typecheck, and build.
- [x] Missing lifecycle helper scripts remain `not_run` in the verification evidence and logged in `BUG-2026-08-07T0118-plan-consistency-gates`.

---

## Review-round-2 audit

- Audited: 2026-08-07
- Scope: `43fc3bc...779b89c`
- Verdict: PASS

- [x] The 256-line standard-library CLI remains below the 300-line limit and has one focused responsibility: fail closed before npm acquisition when the checked-in source boundary is weakened.
- [x] It has no subprocess, shell evaluation, dynamic import, network client, secret, authentication, or application-data path.
- [x] The contract suite separates native npm behavior, project CLI behavior, lockfile failures, and fixed Preflight command ordering; 27 Python tests passed in the full gate.
- [x] Legacy v1, malformed records, forged links, nested overrides, alternate source spellings, configuration arrays, TLS regressions, non-registry URLs, and integrity regressions are all covered by deterministic temporary fixtures.
- [x] The user-approved explicit npm CLI flags narrow the Preflight boundary without adding a package or changing resolved dependency versions.
- [x] Missing lifecycle helper scripts remain honestly `not_run`; the documented bug was not rationalized as a pass.

---

## Review-round-3 audit

- Audited: 2026-08-08
- Scope: `7d09dca...cdf35f4`
- Verdict: PASS

- [x] The classifier now covers gist and Windows-path input with a valid registry lock fixture, so manifest-source coverage is not masked by a bad lockfile.
- [x] Dependency and override shape validation fails closed rather than silently omitting malformed values.
- [x] The test suite checks both exact declared workspace-link acceptance and forged-link rejection; direct exact-version validation includes dependency, dev, optional, and peer fields for dynamically discovered workspaces.
- [x] No dependency, shell invocation, network client, secret, authentication path, dynamic evaluation, or unsafe deserialization was added.
- [x] The full Preflight completed with 29 Python tests, one Node test, five Playwright tests, lint, TypeScript, and production build checks.

---

## Review-round-4 audit

- Audited: 2026-08-08
- Scope: `99c4055...55843db`
- Verdict: PASS

- [x] Effective-policy controls reject release-age exclusions and shrinkwrap substitution before npm runs.
- [x] The added Base64 check verifies an actual 64-byte SHA-512 digest; it introduces no dependency or outbound path.
- [x] Null dependency fields, drive-relative Windows paths, and non-Boolean workspace links fail closed under deterministic fixtures.
- [x] No secret, dynamic evaluation, shell execution, network client, authentication path, or application-data path was added.
- [x] The full Preflight completed with 31 Python tests, one Node test, five Playwright tests, lint, TypeScript, and production build checks.

---

## Post-cap audit

- Audited: 2026-08-08
- Scope: `132e231...dfa8cf1`
- Verdict: PASS

- [x] Generic SCP Git, bare configuration keys, custom CA settings, workspace shrinkwrap, explicit-null links, and weakened minimum age now fail closed under isolated fixtures.
- [x] Supplemental malformed and wrong-length SHA-512 fixtures exercise the decoder without adding a dependency.
- [x] The validator remains standard-library-only and introduces no shell, subprocess, network, secret, authentication, dynamic evaluation, or application-data path.
- [x] The operator explicitly authorized remediation after the ordinary five-round review cap; landing remains gated on an exceptional dual-review pass.
- [x] The full Preflight completed with 31 Python tests, one Node test, five Playwright tests, lint, TypeScript, and production build checks.

---

## Npmrc-normalization audit

- Audited: 2026-08-08
- Scope: `77e67ca...e14694a`
- Verdict: PASS

- [x] Key normalization is bounded to deterministic npmrc text parsing and mirrors the relevant installed npm/ini behavior without importing or adding the JavaScript package.
- [x] Quoted, nested-quoted, inline-comment, bare, scalar, and array forms are covered through the CLI boundary; escaped-comment handling is explicit in the bounded normalizer.
- [x] The correction introduces no dependency, shell, subprocess, network, secret, authentication, dynamic evaluation, or application-data path.
- [x] The full Preflight completed with 31 Python tests, one Node test, five Playwright tests, lint, TypeScript, and production build checks.

---

## Simplified-configuration-boundary audit

- Audited: 2026-08-08
- Scope: `9d66ace...ece907b`
- Verdict: PASS

- [x] The custom npmrc parser and all parser-specific CLI fixtures were removed.
- [x] The source-policy CLI now proves it can validate a source-lock fixture with no `.npmrc` file.
- [x] The project retains one static `.npmrc` defaults contract and literal Preflight npm protections.
- [x] The simplification adds no dependency, shell, subprocess, network, secret, authentication, dynamic evaluation, or application-data path.
- [x] The full Preflight completed with 31 Python tests, one Node test, five Playwright tests, lint, TypeScript, and production build checks.
