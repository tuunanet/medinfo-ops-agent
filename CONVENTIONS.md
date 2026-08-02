# medinfo-ops-agent Conventions

These rules apply to every human and agent contribution.

## Conventional Commits and Versioning

All commits MUST follow Conventional Commits 1.0.0.

Use Semantic Versioning for tagged releases.

Use this commit format:

```text
<type>(<scope>): <description>
```

Use these types:

| Type | Purpose | Version effect |
|------|---------|----------------|
| `feat` | New behavior | Minor |
| `fix` | Defect correction | Patch |
| `perf` | Performance improvement | Patch |
| `docs` | Documentation only | None |
| `test` | Test-only change | None |
| `refactor` | Behavior-preserving restructure | None |
| `chore` | Tooling or maintenance | None |

Mark breaking changes with `!` or a `BREAKING CHANGE:` footer.

NEVER add AI attribution or co-author footers.

## Git Workflow

Use the bigpowers solo-local workflow.

NEVER work directly on `main`.

Start feature work with `kickoff-branch` and a dedicated worktree.

Run release gates through `release-branch` before integration.

Land approved work through `scripts/land-branch.sh`.

Use pull requests only when remote review or CI requires them.

NEVER push directly to `main` outside the guarded landing script.

## Bigpowers Workflow

Agents MUST route work through the relevant bigpowers skill.

Use `survey-context` when project state is unclear.

Use `scope-work`, `slice-tasks`, and `plan-work` before implementation.

Use `develop-tdd` or `execute-plan` for planned implementation.

Use `investigate-bug` before fixing reported defects.

Every implementation task MUST include a runnable `verify` command.

Every completed story MUST include verification evidence.

## Always Green and Shift Left

Preflight MUST pass before forward implementation or integration.

Remote CI MUST pass when remote CI applies.

Treat every reproducible failure as owned project work.

Fix failures early because later fixes cost more and carry greater risk.

Run the complete local gate with:

```bash
make preflight
```

## Discovered Defects

Use this mandatory fix-or-log ladder:

1. Use `quick-fix` for a trivial data-only defect.
2. Use `fix-bug` when investigation or logic changes are required.
3. Log a bug specification when reproduction remains blocked.

Stop forward work while Preflight or required CI remains red.

Ship discovered fixes in separate Conventional Commits.

### Banned dismissive phrases

| Banned phrase | Required action |
|---------------|-----------------|
| Pre-existing issue | Reproduce, then fix or log it. |
| Unrelated to this session | Reproduce, then fix or log it. |
| Not introduced by my changes | Prove isolation, then restore green gates. |
| Out of scope | Scope limits NEVER override a red required gate. |

## Planning and Project Memory

Write all planning output under `specs/`.

Treat YAML cockpit files as operational sources of truth.

Do not duplicate status across planning files.

Read `specs/state.yaml` before continuing active work.

Follow `handoff.next_skill` when it is populated.

Keep requirements, implementation tasks, and verification commands traceable.

Use stable epic identifiers such as `e01`.

Use stable story identifiers such as `e01s01`.

## Architecture

Prefer a modular monolith with explicit internal boundaries.

Organize backend modules by domain capability.

Keep domain rules independent from FastAPI, LangGraph, MCP, and providers.

Put external systems behind thin project-owned interfaces.

Inject dependencies through constructors or parameters.

Keep one primary PostgreSQL database unless an ADR justifies another store.

Use asynchronous processes only for justified operational boundaries.

Record significant architecture decisions in `specs/adr/`.

## Naming and Structure

Use specific names with one clear domain meaning.

Avoid vague names such as `data`, `handler`, `manager`, or `service`.

Use `snake_case` for Python functions, modules, and variables.

Use `PascalCase` for Python classes and Pydantic models.

Use `camelCase` for TypeScript functions and variables.

Use `PascalCase` for React components and TypeScript types.

Name opaque identifiers with explicit `*_id` suffixes.

Store timestamps in UTC.

Organize tests around observable behavior and domain capability.

Avoid shared utility modules without explicit ownership.

## Code Design

Keep functions between 4 and 20 lines when practical.

Keep source files under 300 lines unless an ADR documents an exception.

Give each function one responsibility.

Give each module one cohesive purpose.

Use early returns instead of nested branches.

Limit nesting to two levels.

Express complex conditions through named predicates.

Name side effects explicitly.

Replace logic literals with named constants.

Delete dead code instead of commenting it out.

Leave every touched file cleaner than before.

Use explicit public types.

NEVER use TypeScript `any` without a documented boundary reason.

NEVER expose untyped Python public functions.

## Immutability and Provenance

Treat original intake as immutable.

Treat sanitization revisions as immutable.

Treat submitted draft revisions and approvals as immutable.

Treat evidence snapshots and audit events as immutable.

Create a new revision for every material change.

Link downstream operations to exact input and configuration versions.

NEVER rewrite historical provenance using current configuration.

## Privacy and Data Boundaries

Use fictional and synthetic operational data only.

Keep raw intake inside the secured application boundary.

Send only minimized sanitized representations across AI boundaries.

Fail closed when sanitization cannot establish a safe representation.

NEVER log raw intake, identifiers, credentials, or unrestricted prompts.

Enforce typed field allowlists in every outbound adapter.

Treat every MCP server as a separate trust boundary.

NEVER permit model-generated arbitrary HTTP destinations.

## Safety and Evidence

Represent triage findings independently.

Keep safety findings separate from workflow routing.

NEVER silently suppress adverse-event or product-quality findings.

Use current eligible approved content as authoritative evidence.

Use synthetic public evidence only under controlled supplementation rules.

NEVER use live connector results in operational cases.

Link every generated factual claim to an eligible application-controlled passage.

Block unsupported critical claims.

Block material evidence conflicts until specialist disposition.

Require explicit human approval for an immutable draft revision.

NEVER let an author approve their own material revision.

Require a separate explicit release action after approval.

## Tests

Follow F.I.R.S.T. test principles.

Keep tests fast, independent, repeatable, self-validating, and timely.

Test every new public behavior.

Add a regression test for every fixed defect.

Test boundary values and failure paths.

Test through public interfaces.

Use named fake classes for external I/O.

NEVER use paid providers in ordinary tests.

Keep real-provider evaluations explicit and opt-in.

NEVER skip a test without a documented ambiguity and approved waiver.

Keep held-out evaluation data separate from prompt development.

NEVER alter gold labels to force a passing metric.

## Formatting and Static Analysis

Use Ruff for Python formatting and linting.

Use a strict Python type checker selected during architecture planning.

Use Prettier for TypeScript and Markdown formatting.

Use ESLint for TypeScript and React linting.

Use strict TypeScript compiler settings.

Automate formatting instead of debating style manually.

## Logging and Observability

Use structured JSON for operational logs.

Use plain text only for human-facing command output.

Use opaque identifiers in logs, traces, and metrics.

Record operation purpose, version, timing, status, and cost metadata.

NEVER record secrets or protected content in telemetry.

Mark unavailable checks as `not_run`.

NEVER represent unavailable checks as passed.

## Defensive Code

Implement defensive behavior only where the architecture defines a boundary.

### Rate limiting

Rate-limit public intake, authentication, uploads, connectors, and paid AI operations.

Enforce limits in backend code.

### Retry

Retry transient failures with bounded exponential backoff and jitter.

Use idempotency keys before retrying state-changing operations.

NEVER retry permanent validation failures automatically.

### Circuit breakers

Isolate repeated external dependency failures.

Expose degraded capability status while preserving unrelated workflow functions.

### Timeouts

Set explicit timeouts for network, model, parser, queue, and delivery operations.

Treat unknown outcomes as unknown until reconciliation succeeds.

### Graceful degradation

Preserve the complete manual workflow when optional AI capabilities fail.

Keep lexical approved-content retrieval available without embeddings.

Keep safety escalation available without AI.

## Documentation

Write why a non-obvious decision exists.

Reference the relevant ADR, story, or defect when preserving unusual behavior.

Add intent and one usage example to public docstrings.

Keep README claims aligned with the latest tagged release.

Document deferred capabilities as deferred.

NEVER present roadmap items as implemented behavior.
