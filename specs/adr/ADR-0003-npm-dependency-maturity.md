# ADR-0003: Hold npm dependency resolution for 30 days

- Status: Accepted
- Date: 2026-08-07
- Decision owner: Project owner
- Applies from: e08s01

## Context

The Shai-Hulud npm supply-chain compromise demonstrated that a newly published package version can execute credential-stealing code during ordinary developer installation. The project already commits `package-lock.json` and uses `npm ci --ignore-scripts` in Preflight, but several direct dependency specifications used ranges that could resolve newly published versions during an update.

The project owner selected a rolling 30-day hold. npm 11.16.0 supports the `min-release-age` configuration used by the pinned toolchain.

## Decision

Configure project npm policy to:

- resolve only releases published more than 30 days ago, with no exclusions;
- use exact SemVer direct dependency specifications that match the committed lockfile;
- require a committed npm lockfile v3, exact runtime engines, and strict peer dependencies;
- run dependency installation without lifecycle scripts;
- deny directory, file, git, and remote dependency sources;
- reject root or declared-workspace shrinkwrap files, malformed dependency and override values, directory, tarball-file, Git (including SCP syntax), shorthand-git, gist, Windows-path, remote, non-registry or invalid SHA-512 SRI lock entries, legacy lockfiles, and forged or malformed workspace links through a standard-library manifest-and-lockfile gate before `npm ci`;
- use `https://registry.npmjs.org/` over TLS; and
- pass the release-age, no-script, source-denial, registry, and TLS controls explicitly to the Preflight `npm ci` dry run.

Do not update an existing resolved package version as part of this decision. A dependency update remains a reviewed repository change.

## Consequences

### Positive

- New npm releases receive a 30-day observation period before resolution can select them.
- Direct dependency updates cannot silently float within a SemVer range.
- Dependency install-time code and alternate source schemes are blocked in the ordinary workflow.
- Contract tests and the project source-policy gate make policy removal, a source-spelling bypass, a weakened TLS setting, or an alternate-source lockfile visible before application gates pass.

### Negative

- A required dependency update may be delayed by up to 30 days.
- A security fix published inside the hold cannot be adopted without a new approved policy decision.
- The controls do not prove that an older package or a reviewed lockfile is safe.

## Alternatives

### Depend only on `package-lock.json`

Rejected. The lockfile freezes clean installations but does not prevent a future ranged resolution from selecting a fresh package.

### Use a fixed historical date

Rejected. A fixed date decays as a control and conflicts with the current validated framework baseline. A rolling window retains the required maturity policy.

### Add a third-party supply-chain scanner

Rejected for this story. npm provides the release-age and native source controls; the project adds only a standard-library validator for manifest, lockfile, and scoped-registry regression detection. Scanning, SBOM, signing, and proxy capabilities need separate scope.

### Allow named exceptions

Rejected. This release has no approved exception. An exception changes the security trade-off and requires a new reviewed requirement.

## Validation

Run the deterministic policy contract tests and the full `make preflight` gate with Node.js 24.18.1 and npm 11.16.0. Perform a security review before release.

## References

- <https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem>
- <https://docs.npmjs.com/cli/v11/using-npm/config#min-release-age>
- <https://docs.npmjs.com/cli/v11/commands/npm-ci>
- `specs/epics/e08-npm-dependency-maturity/e08s01-hold-npm-resolutions.md`
- `specs/security/epics/e08/THREAT_MODEL.md`
