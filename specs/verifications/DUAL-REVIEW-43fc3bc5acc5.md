# Dual review 43fc3bc5acc5

- Target: 43fc3bc5acc5af3e11c8f31d84e0e513ac941bd7
- Merge base: 48767d7bb898bc7e09d8baa30548c6d393b36caa
- Verification: `git diff --check origin/main...43fc3bc`
- AND gate: **FAIL** — Reviewer A reported 3 must-fix finding(s).

## Reviewer A

## must-fix
- **Legacy lockfiles bypass validation.** `validate_lockfile_sources()` only reads `packages` (`scripts/check-npm-acquisition-policy.py:151`). A v1 lockfile stores entries in top-level `dependencies`, so a remote or non-SHA-512 legacy entry passes the CLI. Require lockfile v3 or validate legacy entries; fail closed on non-object entries. Add lock-only negative fixtures.
- **Manifest-source detection is incomplete.** The validator scans only `DEPENDENCY_FIELDS` (`:19-24`), excluding resolution-bearing `overrides`, and its prefix classifier permits valid alternate spellings such as `http:attacker.example` and local `.`/backslash paths (`:130-145`). These bypass the claimed all-manifest-source boundary. Scan override specs recursively and robustly reject all directory/git/remote forms; add fixtures.
- **`strict-ssl` can be weakened before npm runs.** It is present in `.npmrc` but absent from `REQUIRED_SETTINGS` (`:8-18`). Changing it to `false` passes the pre-`npm ci` CLI and permits certificate-validation bypass during acquisition. Require `strict-ssl=true` in the CLI.

## should-fix
- Add direct negative tests for each `allow-*=any` regression and an unreviewed workspace link. Current tests verify only the checked-in settings and the positive declared-link case; they do not prove “only declared workspace links” remains enforced.

## consider
- Pass registry/TLS/source-denial settings explicitly to the Preflight `npm ci` command as defense in depth against higher-precedence npm configuration.

## score
38

## verify result
Passed: `git diff --check origin/main...43fc3bc` completed with no output.

## Reviewer B

## must-fix

- `validate_configuration()` misses valid array-form scoped keys such as `@scope:registry[]`; its `endswith(":registry")` check accepts them. Reject canonical scoped-registry keys including `[]` forms and add a fixture.
- `DEPENDENCY_FIELDS` excludes `overrides`, so source specifications in npm overrides are never checked. Recursively validate override specs and test each denied source form there.
- Lock validation is not fail-closed: missing/legacy `packages` data passes, non-object package entries are skipped, and any `link` resolving to a workspace path is accepted without verifying its package name is that workspace’s declared manifest name. Require v3 package records and permit only the exact declared workspace link mapping. Add isolated negative lock-only and forged-link tests.
- `strict-ssl=true` is asserted only by a later contract test, not by the CLI before `npm ci`. Thus `strict-ssl=false` passes the source gate and npm contacts the registry with weakened TLS validation. Add it to `REQUIRED_SETTINGS` and test rejection.

## should-fix

- `test_direct_workspace_dependencies_are_exact_and_locked` hard-codes `apps/web`; discover all declared workspaces so a new workspace can’t introduce ranged direct dependencies without failing Preflight.

## consider

None.

## score

42

## verify result

Passed — `git diff --check origin/main...43fc3bc` completed with no output.

## Cleanup

```json
{
  "worktreeA": "removed",
  "worktreeB": "removed",
  "tempDirectory": "removed"
}
```
