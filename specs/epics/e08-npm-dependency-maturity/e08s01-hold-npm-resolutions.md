STORY KEY: e08s01
TITLE: Hold npm resolutions for 30 days and freeze acquisition
TYPE: feat
CONTEXT: infrastructure
PARENT: e08
STATUS: Refined
AUTHOR: planning-agent   DATE: 2026-08-07
MATURITY: 5
SIZE: M

### 1. Business narrative [locked]

A developer-operator needs the local JavaScript toolchain to resist immediate uptake of freshly published npm releases. The Shai-Hulud campaign demonstrated that a trusted package ecosystem can distribute credential-stealing install-time code quickly. This story adds a bounded, repository-owned maturity hold while retaining the exact versions already validated by the local workspace.

### 2. Value statement [locked]

As a developer-operator, I want npm dependency resolution to exclude releases younger than 30 days and ordinary installation to avoid dependency lifecycle scripts, so that I can reproduce the local workspace without immediately consuming a newly published package.

### 3. Actors and permissions [locked]

- Developer-operator (internal) — performs a reviewed dependency update or runs the local gates.
- npm CLI (system) — resolves and installs the configured package graph.
- npm registry (external package source) — supplies only registry packages recorded in the lockfile.
- Repository gate (system) — rejects a missing or weakened project policy before application gates run.

### 4. Trigger and preconditions [locked]

Trigger: a developer runs an npm dependency command or `make preflight`.

Preconditions:

- Node.js 24.18.1 and npm 11.16.0 are active.
- `package-lock.json` is committed and is the source of resolved third-party versions.
- The existing versions have been resolved and reviewed before this story; the story must not update them.
- The project has no approved exception to the 30-day hold.

### 5. Main flow and business logic [locked]

1. npm reads the version-controlled project configuration.
2. A dependency-resolution command accepts only releases published more than 30 days ago; it fails rather than selecting a younger release.
3. Direct root and workspace dependency specifications identify one exact version each, and the lockfile records the same graph with integrity values.
4. Ordinary installation uses the committed lockfile, denies dependency lifecycle scripts, and permits only npm-registry dependency sources.
5. Preflight checks this boundary before lint, test, and build.

### 6. Alternative flows and exceptions [locked]

1. **Fresh release:** if a requested dependency has no qualifying release older than 30 days, npm exits non-zero and the developer does not bypass the hold.
2. **Manifest-lock drift:** if an exact manifest specification and the lockfile disagree, frozen installation exits non-zero rather than rewriting the lockfile.
3. **Install script:** an install-time dependency script is skipped; explicit project scripts such as `npm test` still run as intended by npm.
4. **Alternate source:** a directory, tarball file, git reference, or remote URL dependency is rejected.
5. **Emergency upgrade:** no bypass is included. A change that needs an exception is a new reviewed requirement.

### 7. Interface elements [locked]

Context: developer tooling only.

Static elements: repository `.npmrc`, package manifests, lockfile, project-owned source-policy CLI, and policy contract tests.

Dynamic elements: npm's normal non-zero error when a dependency cannot meet the 30-day hold.

### 8. Domain model [locked]

Not applicable. The policy protects development-tool acquisition and creates no operational case, evidence, actor, or audit entity.

### 9. Integrations and boundaries [locked]

- Developer workstation to npm CLI — perennial, direction: both.
- npm CLI to `https://registry.npmjs.org/` — perennial, direction: outbound read-only package metadata and locked tarballs.
- npm CLI to dependency lifecycle scripts — prohibited during installation.
- npm CLI to directory, file, git, and arbitrary remote dependency sources — prohibited.

### 10. Background processes [locked]

Not applicable. Resolution and installation are explicit developer commands. This story adds no background process, queue, or scheduler.

### 11. Notifications [locked]

- npm error output — recipient: developer-operator — trigger: fresh-only resolution, source-policy violation, or manifest-lock mismatch.
- Preflight failure — recipient: developer-operator — trigger: missing or weakened dependency policy.

### 12. Audit and logging [locked]

This story records no operational case data. Standard npm command output and debug logs must not contain credentials. The committed manifest, lockfile, policy configuration, contract tests, and review history provide configuration provenance.

### 13. Solution variabilities [locked]

- Minimum npm release age — source: project `.npmrc` — fixed at 30 days for this release.
- Registry — source: project `.npmrc` — fixed to the public npm registry.
- Direct dependency versions — source: root and workspace manifests — exact values must equal the committed lockfile.
- Dependency-source exceptions — source: none; no exemption is permitted in this story.

### 14. Quality attributes *NFR* [locked]

- Reproducibility: `npm ci` must remain frozen by the committed lockfile.
- Determinism: policy contract tests use repository files and make no registry request.
- Gate order: dependency policy validation must occur before lint, test, and build.
- Compatibility: the complete gate must pass on Node.js 24.18.1 and npm 11.16.0.

### 15. Security and compliance *NFR* [locked]

- A 30-day maturity hold applies to every dependency tree resolution; no exception is configured.
- Dependency lifecycle scripts are disabled for ordinary installation.
- Third-party dependencies must come from the npm registry and retain SHA-512 lockfile integrity values.
- The project must not claim that the hold or lockfile makes every dependency safe; older or reviewed compromised packages remain residual risks.
- The implementation receives security review before release.

### 16. UX and accessibility *NFR* [locked]

Not applicable. The user interface is npm and terminal output owned by the package manager.

### 17. Acceptance criteria [locked]

Scenario: Mature-only resolution (SC-e08s01-P0-01)
  Given npm 11.16.0 reads the repository policy
  When a dependency tree is resolved
  Then a release published fewer than 30 days ago is not selected
  And resolution fails if no qualifying release is available

Scenario: Exact reproducible graph (SC-e08s01-P0-02)
  Given a root or workspace direct dependency
  When its manifest and committed lockfile are inspected
  Then the manifest uses an exact SemVer version
  And the specification equals the resolved lockfile version

Scenario: No unreviewed acquisition code or source (SC-e08s01-P0-03)
  Given an ordinary installation
  When npm reads the project policy and lockfile
  Then dependency lifecycle scripts are disabled
  And non-registry directory, file, git, and remote sources are denied
  And each third-party lock entry has an npm-registry URL and SHA-512 integrity value

Scenario: Preflight preserves the policy (SC-e08s01-P0-04, SC-e08s01-P1-01)
  Given the project has the approved dependency policy
  When the developer runs `make preflight`
  Then npm performs a frozen no-script dry run with the 30-day hold before lint, test, and build
  And the full Preflight command passes

### 18. Out of scope [locked]

- Automatically upgrading packages, changing any resolved package version, or adding a dependency.
- Vulnerability scanning, package signing, SBOM generation, a private registry, or artifact mirroring.
- Allowing a release-age or source-policy exception.
- Claims of complete software supply-chain security.

### 19. Open questions [locked]

Not applicable. The project owner approved the 30-day rolling minimum release age and no exception.

### 20. References [locked]

- `specs/product/SCOPE_LATEST.yaml` — IS-08 and SC-15.
- `specs/IMPACT_LATEST.md` — shared-boundary impact assessment.
- `specs/tech-architecture/e08-TEST_PLAN_LATEST.md` — P0 contract scenarios and fixture policy.
- `specs/security/epics/e08/THREAT_MODEL.md` — dependency-acquisition threats and residual risk.
- <https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem> — CISA incident guidance for the Shai-Hulud npm compromise.
- <https://docs.npmjs.com/cli/v11/using-npm/config#min-release-age> — relative npm release-age semantics.
- <https://docs.npmjs.com/cli/v11/commands/npm-ci> — frozen npm installation behavior.

## Requirement deltas [locked]

#### ADDED: R-e08s01-01 Rolling mature-release resolution

The repository must configure npm to resolve only releases published more than 30 days earlier, with no configured exclusion.

#### ADDED: R-e08s01-02 Exact and integrity-bearing dependency graph

Every direct root and workspace dependency must use an exact SemVer specification equal to the committed lockfile resolution. Each third-party lock entry must retain its npm-registry URL and SHA-512 integrity value.

#### ADDED: R-e08s01-03 Frozen, no-script, registry-only installation

The repository must retain a v3 committed lockfile; reject root and declared-workspace npm-shrinkwrap files; disable dependency lifecycle scripts; deny directory, file, Windows-path (including drive-relative), Git (including SCP syntax), shorthand-git, gist, remote, override, and forged or malformed workspace-link sources; reject null or malformed source-bearing manifest structures; require valid SHA-512 SRI; use the public npm registry with strict TLS for third-party dependency acquisition; keep one simple `.npmrc` default-settings contract; and run a deterministic manifest-and-lockfile source-policy gate before explicitly hardened `npm ci`.

#### ADDED: R-e08s01-04 Policy regression gate

Preflight and deterministic contract tests must fail if the 30-day hold or the acquisition controls are removed or weakened.

## Prior Art

| Candidate | Source | Verdict | Notes |
| --- | --- | --- | --- |
| Existing frozen install | `scripts/run-preflight.sh` | extend | It already uses `npm ci --ignore-scripts --dry-run`; retain and add the age hold plus policy contracts. |
| Existing exact runtime pin | `package.json` | extend | npm 11.16.0 is already exact and accepted `--min-release-age=30` in the verified baseline. |
| npm `min-release-age` | npm CLI v11 config documentation | adopt | Use the documented rolling-day policy; do not invent timestamp verification code. |
| CISA Shai-Hulud alert | CISA, 23 September 2025 | compose | Combine its lockfile and safe-release guidance with npm's native maturity control. |

## Implementation steps [locked]

1. Add hermetic P0 contract tests for SC-e08s01-P0-01 through SC-e08s01-P0-03, including behavioral denial and matching manifest/lockfile source fixtures, before changing enforcement → verify: `uv run --locked python -m unittest tests.contract.test_npm_dependency_policy tests.contract.test_npm_acquisition_policy_cli`
2. Add the project npm policy, project-owned source-policy gate, and exact direct workspace specifications without changing any resolved package version (ref: ADR-0003) → verify: `uv run --locked python -m unittest tests.contract.test_npm_dependency_policy tests.contract.test_npm_acquisition_policy_cli`
3. Enforce SC-e08s01-P0-04 by running the source-policy gate before npm and passing all native source-denial and TLS flags explicitly to Preflight `npm ci`; record the dependency-maturity decision (ref: ADR-0003), and confirm no new security findings in affected paths → verify: `make preflight`

## Verification Script (Step-by-Step) [locked]

1. Activate Node.js 24.18.1 with the repository `.nvmrc`.
2. Run `npm config get min-release-age` in the repository and confirm `30`.
3. Run `uv run --locked python -m unittest tests.contract.test_npm_dependency_policy tests.contract.test_npm_acquisition_policy_cli` and confirm all P0 policy contracts pass without a network request.
4. Run `npm ci --ignore-scripts --dry-run --no-audit --no-fund --min-release-age=30` and confirm npm reports an unchanged frozen tree.
5. Run `make preflight` and confirm its lock, lint, test, and build gates pass.
6. Review the security report and confirm it records no unresolved HIGH finding in the affected paths.

## Risks [locked]

- A release-age window can delay an urgent dependency fix. This release intentionally has no exception; a new approved requirement must govern any trade-off.
- A lockfile can still contain a previously approved but compromised package. Integrity and maturity reduce specific attack paths; they do not establish package trust.
- Higher-precedence npm flags can override repository config. Preflight supplies defense-in-depth flags and the repository review gate detects policy changes.
- Blocking install scripts can expose a package that requires build-time setup. The full existing build and test gate detects that regression.

## Zoom-out check [locked]

The root and workspace manifests declare direct JavaScript dependencies; `package-lock.json` freezes their resolved graph; and `scripts/run-preflight.sh` invokes the frozen dependency check before all application gates. Their callers are developer setup, `make preflight`, and every build, lint, and test command. Their contracts are exact Node.js/npm versions, a committed lockfile, deterministic no-script installation, and a working web toolchain.

## Reason for Depth [locked]

The source-policy CLI has one narrow responsibility: reject weakened project configuration or unreviewed dependency-source specifications before npm installs anything. It hides workspace discovery, manifest inspection, and lockfile inspection behind one fixed Preflight command without a new dependency.

## Slopcheck [locked]

- `[OK]` npm 11.16.0 — existing pinned package manager; native `min-release-age` and frozen-install behavior satisfy the requirement without a new dependency.
- No new external package is proposed.

## Red-flag check [locked]

The plan rejects four unsafe shortcuts: relying on the lockfile without removing manifest ranges, treating `npm ci` as a freshness check despite its frozen graph, adding a new supply-chain scanner instead of using npm's native policy, and claiming that a 30-day hold proves all dependencies are safe.
