# Impact Assessment: Final Npm Source-Policy Review Correction

## Target

`scripts/check-npm-acquisition-policy.py`, `scripts/run-preflight.sh`, and the npm policy contract tests make the source-policy boundary independently enforceable before npm installation.

The existing `.npmrc` `allow-directory`, `allow-file`, `allow-git`, and `allow-remote` settings are recognised npm 11.16.0 controls: its installed CLI documentation states that `none` prevents each corresponding source type. The review correctly identified a coverage gap, however: the repository had not proven that behavior or rejected a scoped-registry override in a repository-controlled gate.

## Dependents (8)

1. `Makefile` invokes `scripts/run-preflight.sh` for the shared repository gate.
2. `scripts/run-preflight.sh` performs dependency validation before lint, test, and build.
3. `tests/contract/test_preflight_command.py` asserts the Preflight command sequence.
4. `tests/contract/test_npm_dependency_policy.py` owns the npm policy contracts.
5. `tests/contract/test_root_commands.py` covers the root runtime and lockfile contract.
6. `apps/web` consumes the validated lockfile for build, lint, and browser tests.
7. `e01s01` owns the existing deterministic root-gate contract.
8. All planned application stories depend indirectly on this acquisition boundary.

## Affected Stories

- **e08s01 — Hold npm resolutions for 30 days and freeze acquisition:** direct owner of behavioral source-denial proof and the policy gate.
- **e01s01 — Open a healthy local reviewer workspace:** owns the shared Preflight sequence; no runtime behavior changes.
- **e01s02 through e07s02:** indirect consumers of the resulting install, lint, test, and build gate.

## Test Coverage

- `tests/contract/test_npm_dependency_policy.py` checks the effective release-age setting, every discovered workspace's exact dependency graph, policy text, native directory denial, and current lockfile URLs/integrity.
- `tests/contract/test_npm_acquisition_policy_cli.py` isolates weakened-age, exclusion, custom-CA, alternate-source, malformed-manifest, shrinkwrap, malformed-link, and malformed-SRI fixtures from otherwise-valid lock records.
- `tests/contract/test_preflight_command.py` checks the fixed Preflight npm arguments with a hermetic fake executable.
- Positive coverage proves that the exact declared workspace link remains accepted.

## Risk: High

This remains the shared dependency-acquisition boundary. A source-policy bypass can execute or retrieve unreviewed content before application gates run.

## Recommended action

The post-cap TDD correction is complete: the standard-library policy CLI now rejects generic SCP Git, npm/ini-normalized bare, quoted, comment-suffixed, and array policy keys, custom CA roots, declared-workspace shrinkwrap, explicit-null links, and weakened minimum age. Preserve npm's native denial controls and explicit Preflight flags. Add no dependency, and require a dual-blind pass before landing.
