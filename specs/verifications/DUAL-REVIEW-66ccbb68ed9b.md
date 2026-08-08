# Dual review 66ccbb68ed9b

- Target: 66ccbb68ed9bac41f30487ff3a91de734fd3c693
- Merge base: 48767d7bb898bc7e09d8baa30548c6d393b36caa
- Verification: `git diff --check origin/main...66ccbb6`
- AND gate: **FAIL** — Reviewer A reported 1 must-fix finding(s).

## Reviewer A

## must-fix
- **`.npmrc:13-16` does not enforce alternate-source denial.** `allow-directory`, `allow-file`, `allow-git`, and `allow-remote` are not npm source-policy controls; npm accepts arbitrary config keys, so these values can be read by the contract test without restricting `file:`, git, or remote/tarball dependencies. A reviewed manifest-and-lockfile change can therefore introduce a non-registry source and still pass `npm ci`. Use an actually enforced validation mechanism and run it from Preflight; add behavioral fixtures for each prohibited source.

## should-fix
- **`tests/contract/test_npm_dependency_policy.py:68-85` validates text, not enforcement.** It parses `.npmrc` and treats arbitrary key/value pairs as policy. Add tests that prove prohibited source specs fail the actual policy check, including a matching lockfile case, rather than only checking configuration spelling.

## consider
- The missing baseline lifecycle helper scripts are explicitly and correctly logged as an open, `not_run` non-feature issue; they are not treated as passed checks.

## score
72

## verify result
Passed: `git diff --check origin/main...66ccbb6` completed with no output.

## Reviewer B

## must-fix

- `.npmrc:13-16` uses `allow-directory`, `allow-file`, `allow-git`, and `allow-remote`, which are not npm acquisition-denial controls. npm accepts unknown config keys, so these entries do not prevent `file:`, directory, git, or remote-tarball dependency specs. This fails the registry-only acquisition requirement. Implement an actual enforced manifest/lockfile source-policy gate (and apply it before installation), or use a package-management control that supports these restrictions.
- `tests/contract/test_npm_dependency_policy.py:68-80` only asserts those inert text settings exist. It neither tests rejection of forbidden package specs nor rejects scoped registry configuration (for example, `@scope:registry=...`), which can bypass the default `registry` setting. Add negative fixtures/tests and make the enforcement mechanism reject them.

## should-fix

- `test_preflight_command.py` replaces npm with a fake executable, so it verifies argument spelling/order but not that npm 11.16.0 applies `min-release-age` during the preflight command. Retain the hermetic command test, but add a targeted effective-policy test where feasible.

## consider

- The documented missing baseline lifecycle helper scripts are explicitly logged as an open non-feature issue; they should not be represented as a successful validation of those helpers.

## score

55

## verify result

Passed: `git diff --check origin/main...66ccbb6` produced no output.

## Cleanup

```json
{
  "worktreeA": "removed",
  "worktreeB": "removed",
  "tempDirectory": "removed"
}
```
