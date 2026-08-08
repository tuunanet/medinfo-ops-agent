# Dual review 9d66ace10bb1

- Target: 9d66ace10bb19a99b39ec46b12ceec672a6f9c21
- Merge base: 48767d7bb898bc7e09d8baa30548c6d393b36caa
- Verification: `git diff --check origin/main...9d66ace`
- AND gate: **FAIL** — Reviewer A reported 3 must-fix finding(s).

## Reviewer A

## must-fix

1. **Forbidden keys can bypass normalization via JSON-array coercion** (`scripts/check-npm-acquisition-policy.py:156-165`).
   Appending `'["ca"]'=...`, `'["cafile"]'=...`, or `'["min-release-age-exclude"]'=next` passes the checker because Python renders the parsed list as `"['ca']"`. npm/ini instead uses the JavaScript array as an object key, coercing `["ca"]` to effective key `ca`. Custom trust roots and release-age exclusions can therefore evade the gate.

2. **Environment-expanded keys bypass forbidden-key checks** (`scripts/check-npm-acquisition-policy.py:142-181`).
   npm applies environment replacement to parsed keys. For example, with an unset variable, `c${NPM_POLICY_UNSET?}a=...` becomes effective `ca`, while the checker retains the literal placeholder and passes. This also applies to `cafile`, scoped registries, and release-age exclusions.

3. **`before` can disable the rolling maturity hold** (`scripts/check-npm-acquisition-policy.py:118-138`).
   A project entry such as `before=2099-01-01T00:00:00Z` passes validation while npm specifies that `before` overrides `min-release-age` when both originate from the project configuration. Preflight’s CLI flag protects its dry run, but ordinary project npm resolutions lose the required 30-day hold.

## should-fix

Add differential tests against npm 11.16.0’s effective configuration for JSON-array keys, environment-expanded keys, bracket arrays, bare keys, and escaped `#`/`;`. Current tests exercise the custom checker but omit escaped-comment cases and did not expose the remaining parser differences.

## consider

None.

## score

48

## verify result

Passed: `git diff --check origin/main...9d66ace` completed with no output.

## Reviewer B

## must-fix

1. **The parser does not preserve npm/ini key semantics** (`scripts/check-npm-acquisition-policy.py:142-181`). It lowercases keys and ignores INI sections. Replacing `min-release-age` with `MIN-RELEASE-AGE`, or placing required controls under `[policy]`, passes this validator while npm treats the controls as unknown/nested and uses permissive defaults.

2. **Required array keys bypass native source controls** (`scripts/check-npm-acquisition-policy.py:150`). Appending `allow-directory[]=all` leaves the validator’s separate `allow-directory=none` entry intact, but npm/ini combines both into the effective `allow-directory` array. npm 11.16 then treats a direct directory dependency as root-allowed. Required policy arrays must be folded or rejected using npm’s effective semantics.

3. **`before` can disable the maturity hold.** The validator forbids `min-release-age-exclude` but permits `before=2999-01-01`. npm 11.16 documents and implements same-source `before` as overriding `min-release-age`, allowing fresh releases while the policy CLI still passes. Reject `before`, including quoted, commented, bare, and array forms.

## should-fix

Add real-npm regression fixtures for uppercase keys, INI sections, required-setting arrays, and `before` overrides.

## consider

The quote, nested-quote, inline-comment, escaped `#`/`;`, bare-key, CA, cafile, and explicit `min-release-age-exclude` normalization paths otherwise match the pinned `ini@6` behavior reviewed.

## score

61

## verify result

Passed — `git diff --check origin/main...9d66ace` produced no output.

## Cleanup

```json
{
  "worktreeA": "removed",
  "worktreeB": "removed",
  "tempDirectory": "removed"
}
```
