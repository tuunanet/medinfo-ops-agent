# Review Response: e08s01 Dual Review Round 1

- Review artifact: `DUAL-REVIEW-66ccbb68ed9b.md`
- Gate: FAIL — do not merge

## Findings and disposition

1. **Reviewer A must-fix / Reviewer B must-fix — alternate-source denial is unproven.**
   - **Disposition:** fix.
   - **Correction to premise:** npm 11.16.0 recognises `allow-directory`, `allow-file`, `allow-git`, and `allow-remote`; its installed `npm install` documentation states that `none` prevents each source type. A temporary-project proof also produced `EALLOWDIRECTORY` for `allow-directory=none`.
   - **Gap accepted:** the repository tests only parsed policy text and did not prove source denial or reject future scoped-registry configuration.
   - **Action:** add a standard-library source-policy CLI, execute it before `npm ci`, and add negative fixture coverage for every denied source class and a scoped-registry override.

2. **Reviewer A should-fix / Reviewer B should-fix — contract test validates text rather than behavior.**
   - **Disposition:** fix.
   - **Action:** add a hermetic temporary-project npm behavioral test for directory denial and CLI-level source-policy fixtures containing matching manifest and lockfile entries.

3. **Reviewer B should-fix — fake npm verifies Preflight spelling but not the effective policy.**
   - **Disposition:** fix where deterministic.
   - **Action:** retain the hermetic command-order contract and use real npm 11.16.0 for the directory-denial behavior. Dynamic publication-age resolution remains out of scope for hermetic tests; the existing real `npm config get min-release-age --location=project` test proves the effective project value.

4. **Reviewer A/B consider — unavailable baseline lifecycle helpers are correctly `not_run`.**
   - **Disposition:** no product decision required.
   - **Reason:** this is an observation, not an alternative design. `BUG-2026-08-07T0118-plan-consistency-gates` remains open and the checks will continue to be recorded as unavailable.

## Next gate

Return to TDD for the accepted source-policy coverage and enforcement gap. Re-run the dual-blind AND gate after the corrected implementation passes Preflight.

---

# Review Response: e08s01 Dual Review Round 2

- Review artifact: `DUAL-REVIEW-43fc3bc5acc5.md`
- Gate: FAIL — do not merge

## Findings and disposition

1. **Legacy or malformed lockfile records can bypass the CLI.**
   - **Category:** must-fix.
   - **Action:** require lockfile v3 and an object-shaped `packages` map; add legacy, malformed, non-registry, non-SHA-512, and forged-link fixtures.

2. **Manifest classification omits overrides and alternate spellings.**
   - **Category:** must-fix.
   - **Action:** recursively inspect override values and reject URL-scheme, local-path, tarball, git, and shorthand-git forms; add nested override fixtures.

3. **TLS and scoped-registry configuration can be weakened or encoded with array keys.**
   - **Category:** must-fix.
   - **Action:** require `strict-ssl=true` in the CLI and reject scoped registry keys with or without `[]`.

4. **Workspace links are not tied to the declared workspace package name.**
   - **Category:** must-fix.
   - **Action:** permit a link only when both its target path and `node_modules/<declared-name>` path match a declared workspace; add a forged-link fixture.

5. **Direct dependency coverage is hard-coded to `apps/web`.**
   - **Category:** should-fix.
   - **Action:** discover all declared workspaces in the contract test before checking exact specifications.

6. **Pass source-denial and TLS flags explicitly to `npm ci`.**
   - **Category:** consider.
   - **Disposition:** apply; the project operator approved this defense in depth on 2026-08-07.

## Next gate

Return to TDD for the approved correction, then refresh security, audit, Preflight, and the dual-blind AND gate before landing.

---

# Review Response: e08s01 Dual Review Round 3

- Review artifact: `DUAL-REVIEW-7d09dca14cd7.md`
- Gate: FAIL — do not merge

## Findings and disposition

1. **Gist and Windows-path alternate source forms are permitted.**
   - **Category:** must-fix.
   - **Action:** classify `gist:` as hosted git and drive-letter or backslash paths as directories; add isolated valid-lock fixtures.

2. **Malformed dependency and override shapes are silently ignored.**
   - **Category:** must-fix.
   - **Action:** reject non-object dependency fields, non-string dependency specifications, and non-string/non-object override leaves; add fixtures.

3. **Exact-direct dependency coverage omits optional and peer fields.**
   - **Category:** should-fix.
   - **Action:** include `optionalDependencies` and `peerDependencies` in every dynamically discovered workspace check.

4. **Manifest-source fixtures can be masked by invalid lock sources.**
   - **Category:** should-fix.
   - **Action:** retain otherwise-valid registry lock entries for each manifest classification fixture.

5. **Positive declared-workspace-link fixture.**
   - **Category:** consider.
   - **Disposition:** apply; the project operator approved it on 2026-08-08.

## Next gate

Return to TDD for the approved correction, then refresh security, audit, Preflight, and the dual-blind AND gate before landing.

---

# Review Response: e08s01 Dual Review Round 4

- Review artifact: `DUAL-REVIEW-99c40557c2d6.md`
- Gate: FAIL — do not merge

## Findings and disposition

1. **Null dependency fields and drive-relative Windows paths are accepted.**
   - **Category:** must-fix.
   - **Action:** distinguish absent from explicit null dependency fields and classify `C:source` as a directory; add isolated fixtures.

2. **Malformed integrity and link values are accepted.**
   - **Category:** must-fix.
   - **Action:** require `link is True` and a nonempty, decodable SHA-512 SRI digest of the correct byte length; add fixtures.

3. **Release-age exclusions and shrinkwrap can bypass the effective policy.**
   - **Category:** must-fix.
   - **Action:** reject every `min-release-age-exclude` config-key form and a root `npm-shrinkwrap.json`; add fixtures.

## Next gate

Return to TDD for the required correction. Round 5 is the dual-review cap; a remaining must-fix then requires a human decision before landing.

---

# Review Response: e08s01 Dual Review Round 5

- Review artifact: `DUAL-REVIEW-132e23125355.md`
- Gate: FAIL — do not merge
- Human decision: On 2026-08-08, the project operator instructed the agent to proceed with post-cap remediation.

## Findings and disposition

1. **Generic SCP Git and explicit-null lock links are accepted.**
   - **Category:** must-fix.
   - **Action:** classify `user@host:path` as Git and reject every present link value except exact Boolean `true`; add isolated fixtures.

2. **Custom npm CA trust roots are accepted.**
   - **Category:** must-fix.
   - **Action:** reject project `ca` and `cafile` keys, including array forms; add fixtures.

3. **Declared-workspace shrinkwrap is not rejected.**
   - **Category:** must-fix.
   - **Action:** reject `npm-shrinkwrap.json` at the root and in every discovered workspace; add coverage.

4. **The CLI does not independently require the 30-day hold.**
   - **Category:** should-fix; accepted.
   - **Action:** add `min-release-age=30` to the CLI's required settings and test a weakened value.

5. **Additional malformed SRI coverage.**
   - **Category:** consider; accepted.
   - **Action:** add malformed Base64 and wrong-length SHA-512 fixtures.

## Next gate

Return to TDD, refresh all evidence, and run one operator-authorized exceptional dual review. Landing remains prohibited until both reviewers pass with zero must-fix findings.

---

# Review Response: e08s01 Exceptional Review

- Review artifact: `DUAL-REVIEW-77e67ca4bc2a.md`
- Gate: FAIL — do not merge

## Findings and disposition

1. **Quoted and comment-suffixed npmrc keys bypass the policy parser.**
   - **Category:** must-fix.
   - **Action:** normalize npmrc keys with npm/ini quote, comment, and escape semantics; add isolated quoted and comment-suffixed exclusion and CA fixtures.

2. **Array exclusion behavior lacks a direct fixture.**
   - **Category:** should-fix; accepted.
   - **Action:** add `min-release-age-exclude[]=...` coverage.

## Next gate

Return to TDD and refresh all evidence. Landing remains prohibited until both independent reviewers pass with zero must-fix findings.
