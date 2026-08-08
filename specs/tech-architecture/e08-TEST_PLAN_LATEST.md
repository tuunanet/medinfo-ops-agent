# Test Design: e08 — Npm Dependency Maturity and Acquisition Controls

## 1. Risk Matrix and Scenarios

| Scenario ID | Behavior | Risk | Test level | Target |
| --- | --- | --- | --- | --- |
| SC-e08s01-P0-01 | The project-owned npm configuration sets `min-release-age=30`, and npm 11.16.0 reads that project value. | P0 | Contract | `.npmrc`, `tests/contract/test_npm_dependency_policy.py` |
| SC-e08s01-P0-02 | Every direct dependency in each workspace has an exact SemVer specification equal to its lockfile version. | P0 | Contract | `package.json`, `apps/web/package.json`, `package-lock.json` |
| SC-e08s01-P0-03 | Real npm rejects a denied directory source; the project source-policy CLI rejects directory and drive-relative Windows paths, tarball-file, Git (including SCP syntax), shorthand-git, gist, remote, override, root or declared-workspace shrinkwrap, legacy-lock, forged or malformed workspace-link (including explicit null), non-registry, invalid SHA-512 SRI, and malformed or null dependency or override fixtures. It requires lockfile v3 and validates exact declared workspace links. | P0 | Contract | `scripts/check-npm-acquisition-policy.py`, `package-lock.json`, `tests/contract/test_npm_dependency_policy.py`, `tests/contract/test_npm_acquisition_policy_cli.py` |
| SC-e08s01-P0-04 | Preflight performs a frozen `npm ci` dry run with the 30-day hold and no dependency lifecycle scripts before application gates. | P0 | Contract | `scripts/run-preflight.sh`, `tests/contract/test_preflight_command.py` |
| SC-e08s01-P1-01 | The complete root Preflight gate remains green with Node.js 24.18.1 and npm 11.16.0. | P1 | Integration | `make preflight` |

## 2. Fixture Architecture and Isolation

- Use real, repository-versioned JSON and `.npmrc` text as fixtures; do not contact npmjs.com from unit tests.
- Use repository-versioned JSON fixtures for source-policy CLI tests; include root and workspace shrinkwrap, legacy v1, null and malformed dependency or override shapes, non-registry, malformed or wrong-length SHA-512 SRI, nested override, gist, SCP Git, drive-relative Windows-path, forged, null, or non-Boolean link, and valid declared-link cases. Keep manifest-source cases paired with an otherwise valid registry lock record. Fixtures make no registry request.
- Keep exactly one repository `.npmrc` contract that asserts its intended project defaults. Preflight independently enforces its acquisition boundary with literal npm CLI arguments; do not reimplement npmrc parsing.
- Use a temporary project with real npm 11.16.0 to prove that `allow-directory=none` rejects a local directory dependency before installation.
- Treat the sole workspace path, `apps/web`, as the only allowed non-registry lock entry. It is a repository workspace, not a third-party package.
- Run the source-policy CLI in Preflight before its frozen `npm ci --dry-run`; pass the native source-denial and TLS flags explicitly to that `npm ci` command as defense in depth against higher-precedence configuration.

## 3. NFR Verification

| NFR | Requirement | Verification command |
| --- | --- | --- |
| Fresh-package quarantine | npm resolves only releases at least 30 days old. | `uv run --locked python -m unittest tests.contract.test_npm_dependency_policy` |
| Reproducibility | Direct specifications match the committed lockfile and a clean install is frozen under explicit source and TLS controls. | `npm ci --ignore-scripts --dry-run --no-audit --no-fund --min-release-age=30 --allow-directory=none --allow-file=none --allow-git=none --allow-remote=none --strict-ssl=true --registry=https://registry.npmjs.org/` |
| Install-time code and source containment | Dependency lifecycle scripts cannot run and repository manifests, lockfiles, and registry settings cannot introduce a denied source. | `uv run --locked python -m unittest tests.contract.test_npm_dependency_policy` |
| Regression safety | Existing build, lint, test, and runtime contracts remain green. | `make preflight` |

## 4. External Evidence

- CISA's 23 September 2025 alert on the Shai-Hulud npm supply-chain compromise advises a dependency review, lockfile inspection, and pinning known-safe releases.
- npm CLI v11 documents `min-release-age` as a relative number of days: npm tree resolution accepts only releases available more than that many days ago and fails when no qualifying version exists.
- npm CLI v11 documents that `npm ci` requires a lockfile, fails on manifest-lock mismatch, never writes the lockfile, and is therefore a frozen installation.

## 5. Out of Scope

- Vulnerability scanning, an SBOM, a private package proxy, package signing infrastructure, and automatic dependency updates.
- Verifying dynamic registry publication timestamps from ordinary unit tests.
- Allowing exceptions to the 30-day hold in this release.
