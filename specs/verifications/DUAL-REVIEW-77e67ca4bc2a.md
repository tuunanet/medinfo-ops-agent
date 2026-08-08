# Dual review 77e67ca4bc2a

- Target: 77e67ca4bc2a7e9b1fe655cf497f6ad67ee88106
- Merge base: 48767d7bb898bc7e09d8baa30548c6d393b36caa
- Verification: `git diff --check origin/main...77e67ca`
- AND gate: **FAIL** — Reviewer A reported 1 must-fix finding(s).

## Reviewer A

## must-fix
- `scripts/check-npm-acquisition-policy.py:142-152`: `parse_npmrc` does not follow npm/ini key parsing. npm unquotes quoted keys and strips inline `#`/`;` suffixes, but this parser retains them. Appending `"min-release-age-exclude"=source-fixture` or `"cafile"=/tmp/unreviewed.pem` to an otherwise-valid fixture lets this CLI pass while npm applies the forbidden exclusion or custom CA file. Normalize keys according to npmrc semantics and add isolated negative fixtures for these forms.

## should-fix
None

## consider
None

## score
72

## verify result
Passed: `git diff --check origin/main...77e67ca` produced no output.

## Reviewer B

## must-fix
None

## should-fix
- `tests/contract/test_npm_acquisition_policy_cli.py`: add an isolated `min-release-age-exclude[]=...` fixture. The implementation rejects array keys, but this P0 behavior lacks direct regression coverage.

## consider
None

## score
97

## verify result
Passed: `git diff --check origin/main...77e67ca` produced no output.

## Cleanup

```json
{
  "worktreeA": "removed",
  "worktreeB": "removed",
  "tempDirectory": "removed"
}
```
