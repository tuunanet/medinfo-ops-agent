# Dual review 7d09dca14cd7

- Target: 7d09dca14cd7eb205055bffbd71f9546f88f08a1
- Merge base: 48767d7bb898bc7e09d8baa30548c6d393b36caa
- Verification: `git diff --check origin/main...7d09dca`
- AND gate: **FAIL** — Reviewer A reported 2 must-fix finding(s).

## Reviewer A

## must-fix

- `scripts/check-npm-acquisition-policy.py:27,186-203` misses valid alternate sources: `gist:<id>` hosted-git shorthand and Windows drive paths such as `C:\source` return permitted. Both violate the directory/git denial requirement. Add classification and isolated fixtures using otherwise-valid registry lock entries.
- `scripts/check-npm-acquisition-policy.py:163-182` silently ignores malformed dependency fields and override nodes. For example, `optionalDependencies: []` or `overrides: {"x": []}` passes the CLI rather than failing closed. Validate field/map/value shapes and add negative tests.

## should-fix

- `tests/contract/test_npm_dependency_policy.py:58` checks exact versions only for `dependencies` and `devDependencies`; include `optionalDependencies` and `peerDependencies`.
- Several `SOURCE_CASES` fixtures make both manifest and lockfile invalid, so lock validation can mask a regression in manifest-source validation. Isolate each manifest-source test with a valid official-registry SHA-512 lock record.

## consider

- Add a positive fixture for a valid declared workspace link; the current repository lockfile does not exercise the allowed-link branch.

## score

68

## verify result

Passed: `git diff --check origin/main...7d09dca` completed with no output.

## Reviewer B

## must-fix
- `scripts/check-npm-acquisition-policy.py:186` does not classify npm’s `gist:<id>` hosted-Git syntax (and misses drive-letter paths such as `C:\source`). Those sources can pass the manifest/override policy check when paired with an otherwise registry-only lockfile. Reject these forms and add fixtures that isolate manifest/override classification with a clean lockfile.
- `scripts/check-npm-acquisition-policy.py:163-181` silently treats malformed dependency fields, non-string dependency specs, and non-string/non-object override leaves as absent. The source-policy gate must fail closed with errors for these values, rather than reporting success without validating the required dependency fields and recursive overrides. Add negative fixtures for each shape.

## should-fix
None.

## consider
None.

## score
70

## verify result
Passed: `git diff --check origin/main...7d09dca` exited 0 with no output.

## Cleanup

```json
{
  "worktreeA": "removed",
  "worktreeB": "removed",
  "tempDirectory": "removed"
}
```
