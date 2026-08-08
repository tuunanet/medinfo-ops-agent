# Security Review

- Status: Pass
- Date: 2026-08-03
- Scope: `e4fca64...HEAD` release candidate
- Confidence threshold: 8/10

## Result

No unresolved HIGH, MEDIUM, or LOW security finding was identified in the e01s01 diff.

## Evidence

- `specs/security/e01s01t02-security-review.md` covers FastAPI readiness and the rootless Podman database boundary.
- `specs/security/e01s01t04-security-review.md` covers hybrid host-process orchestration, configuration loading, process cleanup, and build commands.
- `specs/security/e01s01t05-security-review.md` covers lint, lockfile, Preflight, and paid-provider isolation gates.
- `specs/security/BUG-2026-08-03T090526-fresh-runtime-database-password-security-review.md` covers credential validation, process arguments, logs, file permissions, and role synchronization.
- `specs/security/BUG-2026-08-03T131144-failed-database-start-cleanup-security-review.md` covers failed-start rollback, listener cleanup, failure status preservation, and volume retention.
- `specs/security/BUG-2026-08-03T131145-contradictory-readiness-payload-security-review.md` covers fail-closed cross-field response validation.
- `npm audit --audit-level=high` reports zero vulnerabilities.
- The final diff contains no committed credential, private key, provider token, unsafe shell evaluation, dynamic SQL, unsafe deserialization, user-controlled remote host, or browser HTML injection sink.
- The cleanup-marker gap fix changes test fixtures only and has no production security path.
- The fresh-runtime fix passes credentials only through validated local configuration and container standard input.
- The failed-start fix removes the project listener and container process while retaining the named data volume.
- The readiness parser rejects every response combination that the backend readiness contract cannot emit.
- Release-only additions after the final implementation review are tests, trace comments, and verification evidence; they add no runtime security path.

## Gate

No finding at confidence 8/10 or higher blocks verification.

---

# Security Review: e08s01 Npm Dependency Maturity and Acquisition Controls

- Status: Pass
- Date: 2026-08-07
- Scope: `origin/main...HEAD` for `.npmrc`, workspace manifests, `package-lock.json`, Preflight, and policy contract tests
- Confidence threshold: 8/10

## Result

No unresolved HIGH finding at confidence 8/10 or higher was identified in the e08s01 implementation diff.

## Assessment

- The only changed executable shell path is the fixed, developer-authored Preflight command. It contains no attacker-controlled interpolation, credential exposure, or new network destination.
- The npm policy fixes the registry to HTTPS, disables install-time dependency scripts, and denies directory, file, git, and remote sources. These changes reduce rather than add package-acquisition attack paths.
- Every direct dependency range was narrowed to the existing lockfile version. A version comparison against `origin/main` found zero resolved package-version changes.
- Contract tests parse repository-controlled manifests and invoke npm with a fixed configuration query. They do not evaluate untrusted content, deserialize untrusted data, or make a request to an attacker-controlled endpoint.
- The 30-day hold cannot prove that an older package or a reviewed lockfile is safe, and higher-precedence npm configuration can be supplied by a trusted local operator. The ADR and threat model record these residual risks without claiming complete supply-chain security.

## Gate

No new security findings in affected paths. No finding at confidence 8/10 or higher blocks verification.

---

# Security Review: e08s01 Source-Policy Enforcement Correction

- Status: Pass
- Date: 2026-08-07
- Scope: `66ccbb6...62bceae` plus the source-policy test and Preflight changes
- Confidence threshold: 8/10

## Result

No unresolved HIGH finding at confidence 8/10 or higher was identified after addressing the first dual-review round.

## Assessment

- npm 11.16.0 treats `allow-directory`, `allow-file`, `allow-git`, and `allow-remote` as real source controls. The installed npm CLI documentation describes `none` as denying the corresponding fetch type; the new temporary-project contract test proves the directory denial with real npm.
- `scripts/check-npm-acquisition-policy.py` uses only the Python standard library, reads repository-controlled text and JSON, starts no subprocess, and makes no network request. A malformed configuration or lockfile fails Preflight rather than allowing npm acquisition.
- The validator requires all native source controls, the official HTTPS registry, and no scoped-registry setting. It scans root and declared workspaces for directory, file, git, and remote specifications, then rejects third-party lock entries without the official registry URL and SHA-512 integrity.
- The Preflight shell path supplies a fixed script path before `npm ci`; it introduces no user-controlled command interpolation or new outbound host.
- The validator permits only lockfile links resolved to declared repository workspaces. Other links fail closed, so local dependency substitution cannot be represented as an npm-registry package.

## Residual risk

A trusted local operator can still supply higher-precedence npm configuration or alter repository controls. The project source gate validates the checked-in files before installation, and changes to those files remain reviewed repository changes; this does not claim complete protection from a compromised trusted workstation.

## Gate

No finding at confidence 8/10 or higher blocks verification or renewed independent review.

---

# Security Review: e08s01 Source-Policy Enforcement Round 2

- Status: Pass
- Date: 2026-08-07
- Scope: `43fc3bc...779b89c` plus current decision records
- Confidence threshold: 8/10

## Result

No unresolved HIGH finding at confidence 8/10 or higher was identified after the second dual-review correction.

## Assessment

- The validator fails closed unless `package-lock.json` is v3 with an object-shaped `packages` map. It rejects malformed records, non-registry URLs, missing SHA-512 integrity, and workspace links whose lockfile path does not match the declared workspace package name.
- It validates all declared workspace manifests and recursively examines override specifications. URL-scheme, local-path, tarball-file, git, shorthand-git, remote, and scoped-registry forms are rejected without starting a subprocess or network request.
- The policy now requires `strict-ssl=true` before npm runs. Preflight repeats the source-denial, TLS, registry, release-age, and no-script controls as literal npm arguments, so a higher-precedence configuration cannot weaken that gate's npm invocation.
- The standard-library CLI only reads supplied project files and emits errors. It performs no shell evaluation, dynamic import, authentication, logging of protected data, or outbound request.
- Contract fixtures exercise each newly identified bypass class, while a real npm temporary-project test confirms the native directory-source denial remains effective.

## Residual risk

A person able to change the repository, execute npm with unrelated flags, or compromise the developer workstation remains a trusted-boundary risk. The controls reduce unreviewed source acquisition in the repository and Preflight paths; they do not establish that older registry packages are benign.

## Gate

No finding at confidence 8/10 or higher blocks verification or renewed independent review.

---

# Security Review: e08s01 Source-Policy Enforcement Round 3

- Status: Pass
- Date: 2026-08-08
- Scope: `7d09dca...cdf35f4` plus current decision records
- Confidence threshold: 8/10

## Result

No unresolved HIGH finding at confidence 8/10 or higher was identified after the third dual-review correction.

## Assessment

- The source classifier now denies hosted-git `gist:` and Windows drive or backslash directory forms in addition to previously covered source forms. Each new form is paired with an otherwise-valid registry lock fixture, preventing lock errors from masking a manifest validation regression.
- Every present source-bearing dependency field must be an object with string package names and specifications. Overrides must be recursively composed of strings or objects. Invalid shapes produce an error before npm runs.
- Lockfile link acceptance is exercised both positively and negatively: only `node_modules/<declared-workspace-name>` resolving to the declared workspace path is permitted.
- The validator remains a standard-library, no-network, no-subprocess read-only gate. The explicit npm source, registry, and TLS flags remain fixed in Preflight.

## Residual risk

Repository-write access, unrelated npm invocation flags, and a compromised developer workstation remain trusted-boundary risks. The project does not claim that these controls establish package trust or neutralize an already compromised older registry package.

## Gate

No finding at confidence 8/10 or higher blocks verification or renewed independent review.

---

# Security Review: e08s01 Effective-Policy Enforcement Round 4

- Status: Pass
- Date: 2026-08-08
- Scope: `99c4055...55843db` plus current decision records
- Confidence threshold: 8/10

## Result

No unresolved HIGH finding at confidence 8/10 or higher was identified after the fourth dual-review correction.

## Assessment

- The gate rejects both scalar and array release-age exclusions and refuses a root `npm-shrinkwrap.json`, so Preflight validates the only effective reviewed lockfile.
- Explicit null source-bearing dependency fields fail as malformed. Drive-relative Windows paths are rejected with other directory forms.
- Workspace links require the Boolean value `true`; all other link values fail. Lock integrity must decode as a 64-byte SHA-512 SRI digest rather than merely start with `sha512-`.
- The validator remains local, standard-library-only, no-network, and no-subprocess. The fixed Preflight npm arguments retain the age, source, registry, TLS, and lifecycle protections.

## Residual risk

Repository-write access, unrelated npm invocation flags, and a compromised developer workstation remain trusted-boundary risks. The project does not claim that these controls establish package trust or neutralize an already compromised older registry package.

## Gate

No finding at confidence 8/10 or higher blocks verification or the fifth independent review.

---

# Security Review: e08s01 Post-Cap Source-Policy Enforcement

- Status: Pass
- Date: 2026-08-08
- Scope: `132e231...dfa8cf1` plus current decision records
- Confidence threshold: 8/10

## Result

No unresolved HIGH finding at confidence 8/10 or higher was identified after the operator-authorized post-cap correction.

## Assessment

- Dependency specifications now reject generic SCP Git forms with or without an explicit user. Bare npmrc keys are parsed fail-closed rather than ignored.
- The gate independently requires `min-release-age=30`; it rejects scalar, array, and bare exclusion keys and every project `ca` or `cafile` form covered by npmrc syntax.
- Root and every discovered workspace are checked for `npm-shrinkwrap.json`, preventing an alternate effective lock graph in a declared workspace.
- Every present lockfile `link` field must be exact Boolean `true` and match the declared workspace name and path. Registry packages cannot carry `link: null`. SHA-512 SRI must be valid Base64 decoding to exactly 64 bytes.
- The validator remains standard-library-only, local, read-only, no-network, and no-subprocess. It adds no application data, authentication, secret, or dynamic execution path.

## Residual risk

Repository-write access, unrelated npm invocations, global workstation trust configuration, and a compromised developer workstation remain trusted-boundary risks. The controls do not establish package trust or neutralize a compromised package older than 30 days.

## Gate

No finding at confidence 8/10 or higher blocks the operator-authorized exceptional independent review.

---

# Security Review: e08s01 Npmrc Normalization Correction

- Status: Pass
- Date: 2026-08-08
- Scope: `77e67ca...e14694a` plus current decision records
- Confidence threshold: 8/10

## Result

No unresolved HIGH finding at confidence 8/10 or higher was identified after the npmrc normalization correction.

## Assessment

- The parser now normalizes keys with the npm `ini` package's relevant semantics: matching quotes are decoded, unescaped `#` and `;` terminate keys, and escaped comment characters remain literal.
- Isolated fixtures cover scalar and array release-age exclusions plus bare, double-quoted, single-quoted, nested-quoted, hash-suffixed, and semicolon-suffixed forbidden keys.
- Required values and forbidden-key decisions operate on normalized lowercase keys, closing the mismatch between npm's effective configuration and the pre-npm gate.
- The correction uses the existing Python standard library and adds no network, subprocess, secret, dynamic evaluation, authentication, or application-data path.

## Residual risk

Repository-write access, unrelated npm invocations, global workstation trust configuration, and a compromised developer workstation remain trusted-boundary risks. These controls do not prove package safety.

## Gate

No finding at confidence 8/10 or higher blocks renewed independent review.

---

# Security Review: e08s01 Simplified Configuration Boundary

- Status: Pass
- Date: 2026-08-08
- Scope: `9d66ace...ece907b` plus current decision records
- Confidence threshold: 8/10

## Result

No unresolved HIGH finding at confidence 8/10 or higher was identified.

## Assessment

- The project-owned validator no longer parses or attempts to emulate npm configuration. It validates only repository manifests, declared-workspace links, shrinkwrap absence, and lockfile source and integrity data.
- The repository `.npmrc` is asserted by a simple contract. Preflight independently uses literal age, source-denial, registry, TLS, and no-script npm CLI arguments.
- A positive fixture proves the source-lock validator operates without `.npmrc`, preventing configuration-parser regressions from reentering this execution boundary.
- The simplification removes local parsing logic and adds no dependency, network, subprocess, secret, dynamic evaluation, authentication, or application-data path.

## Residual risk

Repository-write access, unrelated npm invocations, and a compromised developer workstation remain trusted-boundary risks. These controls do not prove package safety.

## Gate

No finding at confidence 8/10 or higher blocks independent review.

---

# Security Review: e08s01 Mandatory Workspace Links

- Status: Pass
- Date: 2026-08-08
- Scope: `5ff7537...1c3225c`

The lockfile gate now requires each declared workspace to have exactly the expected `node_modules/<workspace-name>` record with `link: true` and its declared workspace resolution. Missing and registry-shaped replacement records fail under isolated fixtures. This adds no dependency or execution path.

## Gate

No finding at confidence 8/10 or higher blocks independent review.
