# e08 Threat Model: Npm Dependency Maturity and Acquisition Controls

## Scope

The story changes repository-controlled npm resolution and installation policy. It does not add an application endpoint, credentials, or a new provider.

## Assets

- Developer workstation credentials and source-tree integrity exposed during dependency installation.
- The version-controlled JavaScript dependency graph used by local gates.
- The deterministic build, test, and lint environment shared by all planned stories.

## Threats and controls

| Threat | Attack path | Control | Verification |
| --- | --- | --- | --- |
| Fresh malicious npm release | A broad dependency range resolves to a recently published compromised version. | `min-release-age=30`, exact direct specifications, and committed lockfile. | SC-e08s01-P0-01 and SC-e08s01-P0-02 |
| Install-time credential theft | A dependency `preinstall`, `install`, `postinstall`, or `prepare` script runs during setup. | Project `ignore-scripts=true` plus explicit no-script preflight invocation. | SC-e08s01-P0-03 and SC-e08s01-P0-04 |
| Unreviewed alternate source | A manifest, shrinkwrap, or lockfile fetches a local directory, Windows path, tarball, Git reference (including SCP syntax), shorthand-git, gist, arbitrary remote URL, manifest override, legacy lock record, forged or malformed workspace link, or scoped-registry override. | npm's native source denials plus a fail-closed project manifest-and-lockfile v3 source-policy gate before `npm ci`; reject root and declared-workspace shrinkwrap files and malformed source-bearing fields; require exact Boolean declared workspace links, npmjs registry URLs, and valid 64-byte SHA-512 SRI digests. | SC-e08s01-P0-03 |
| TLS downgrade or silent policy regression | A future edit weakens the committed defaults or changes a source restriction while application tests still pass. | A simple repository `.npmrc` contract checks committed defaults. Preflight passes literal native npm age, source, registry, TLS, and no-script flags, while the source-policy gate validates manifests and lockfiles. | SC-e08s01-P0-01 through SC-e08s01-P0-04 |

## Residual risk

A 30-day hold reduces exposure to newly released malware; it cannot establish that an older package or a reviewed lockfile is benign. A person able to modify repository configuration or pass higher-precedence npm flags can override local policy. Lockfile changes therefore remain human-reviewed changes, and the project does not claim complete supply-chain security.

## Security level

**High.** This is an execution boundary before the application starts. The story must receive a security review after implementation and before release.
