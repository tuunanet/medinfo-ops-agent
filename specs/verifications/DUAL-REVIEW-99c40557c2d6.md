# Dual review 99c40557c2d6

- Target: 99c40557c2d66d86c01ed26adbd7057644bbecda
- Merge base: 48767d7bb898bc7e09d8baa30548c6d393b36caa
- Verification: `git diff --check origin/main...99c4055`
- AND gate: **FAIL** — Reviewer A reported 3 must-fix finding(s).

## Reviewer A

## must-fix
- `scripts/check-npm-acquisition-policy.py:169-171` silently accepts explicitly present dependency fields set to JSON `null`. A valid fixture with `"dependencies": null` and an otherwise valid registry lock exits successfully, despite the required fail-closed object shape. Reject `null` when the field is present; add isolated null fixtures.
- `scripts/check-npm-acquisition-policy.py:221` misses drive-relative Windows paths such as `C:source`: its slice is `:s`, so the source is allowed. This is a Windows local-directory form and violates the required Windows-path denial. Add a `C:source` fixture with a valid lock.
- Lock validation is not fail-closed for malformed integrity/link shapes: `link: "true"` is accepted as a workspace link at `:263`, and `integrity: "sha512-"` is accepted at `:277`. Require `link is True` and validate a nonempty valid SHA-512 SRI digest; add negative fixtures.

## should-fix
None

## consider
None

## score
58

## verify result
Passed: `git diff --check origin/main...99c4055` completed with no output.

## Reviewer B

## must-fix
- `min-release-age-exclude=next` bypasses the 30-day hold. The validator does not reject this non-array npm config form, tests only check `min-release-age-exclude[]`, and Preflight’s `--min-release-age=30` does not clear exclusions. Reject all exclusion-key forms and test them.
- `npm-shrinkwrap.json` is ignored by the validator, although npm prefers it over `package-lock.json` for `npm ci`. Adding a shrinkwrap with an alternate graph/source leaves the CLI checking only the benign package lock. Reject a root shrinkwrap or validate the effective lockfile; add coverage.
- Explicit `null` dependency fields pass validation: `manifest_specifications()` treats both absent and present-`null` fields as `None` and skips them. A valid fixture with `"optionalDependencies": null` exits successfully. Check field presence separately and reject null/non-object values.
- Lock validation accepts malformed trusted fields: `integrity: "sha512-"` passes the prefix check, and a declared workspace link with `"link": "true"` passes truthiness checking. Require a valid SHA-512 SRI digest and `link is True`; add negative fixtures.

## should-fix
None

## consider
None

## score
52

## verify result
Passed — `git diff --check origin/main...99c4055` completed with no output.

## Cleanup

```json
{
  "worktreeA": "removed",
  "worktreeB": "removed",
  "tempDirectory": "removed"
}
```
