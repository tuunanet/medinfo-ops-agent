# e01s01 Coverage Gate

- Status: Pass
- Date: 2026-08-03
- Numeric scope: executable branch-bearing readiness business logic
- Overall measured coverage: 100%
- Business logic coverage: 100%

## Python readiness logic

Command:

```bash
uv run --locked --with 'coverage==7.10.7' coverage run --branch \
  --source=services/api -m unittest discover -s tests/api -p 'test_*.py'
uv run --locked --with 'coverage==7.10.7' coverage report --show-missing
```

Result: 76 statements, four branches, zero misses, 100% coverage.

## TypeScript readiness logic

Command:

```bash
node --experimental-test-coverage --test tests/web/readiness.test.ts
```

Result for `apps/web/src/readiness.ts`: 100% lines, 100% branches, and 100% functions.

## Integration coverage

The numeric denominator excludes shell orchestration and declarative React rendering because this repository has no trustworthy line instrumenter for those boundaries. It does not claim whole-repository line coverage. Their observable behavior is covered by 11 Python contract tests and five Playwright Chromium scenarios, plus the manual UAT recorded in `specs/verifications/e01s01-verify.yaml`.

The release thresholds apply to the instrumented executable business logic: overall measured coverage is at least 80%, and business logic coverage is at least 95%.
