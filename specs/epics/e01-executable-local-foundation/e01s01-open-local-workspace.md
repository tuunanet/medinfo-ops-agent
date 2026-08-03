STORY KEY: e01s01
TITLE:     Open a healthy local reviewer workspace
TYPE:      Story
PARENT:    e01
STATUS:    Refined
AUTHOR:    planning-agent   DATE: 2026-08-01
MATURITY:  5
SIZE:      M

### 1. Business narrative [locked]

A fictional medical-information reviewer needs one dependable local entry point before any case workflow can be trusted. The current repository contains plans but no runnable product, so later privacy, authorization, evidence, and audit stories have no executable boundary to extend.

The first usable increment must report its condition honestly. A visible page must distinguish a live application from one that is ready to use. Database or extension failure must remain visible rather than being hidden behind a successful page load.

### 2. Value statement [locked]

As a fictional reviewer, I want to open a local workspace with truthful readiness status, so that I know whether the product is safe to use for synthetic work.

### 3. Actors and permissions [locked]

- Reviewer (internal) — view local service readiness and failure guidance. This story grants no case permissions.
- Developer-operator (internal) — start, stop, test, build, lint, and verify the local workspace.
- Web application (system) — request and display API readiness without inventing fallback success.
- API application (system) — report process liveness and dependency readiness without exposing credentials.
- PostgreSQL service (system) — provide transactional connectivity and the pgvector extension.

All actors and operational representations remain fictional or system-local.

### 4. Trigger and preconditions [locked]

Trigger: the developer-operator invokes `make dev` from the repository root.

Preconditions:

- Python 3.14.6 is available through `uv` and `.python-version`.
- Node.js 24.18.1 is active and matches `.nvmrc` and the package engine constraint.
- Rootless Podman 5.7.0 or newer can start the pinned PostgreSQL 18 and pgvector 0.8.6 OCI image.
- Python dependencies are locked in `uv.lock`.
- Node.js dependencies are locked in `package-lock.json`.
- No paid-provider credential is required.

### 5. Main flow and business logic [locked]

1. The command contract checks the required Python, Node.js, package-manager, and container tools.
2. Direct rootless Podman commands start the PostgreSQL/pgvector container.
3. The database initializes the `vector` extension idempotently.
4. The host starts FastAPI and Next.js development processes.
5. FastAPI reports process liveness independently from dependency readiness.
6. FastAPI reports ready only when PostgreSQL is reachable and the `vector` extension exists.
7. The Next.js workspace requests API readiness and displays API and database status.
8. The reviewer sees either an explicit ready state or actionable unavailable state.

Interruption point: N/A — a failed cold start is stopped and retried from the root command.

### 6. Alternative flows and exceptions [locked]

1. **6a — Runtime mismatch:** a Python or Node.js version mismatch stops before service startup and names the required and detected versions.
2. **6b — Database unavailable:** API liveness remains successful, API readiness returns HTTP 503, and the workspace does not display ready.
3. **6c — pgvector unavailable:** API readiness returns HTTP 503 even when PostgreSQL accepts connections.
4. **6d — API unavailable:** the workspace displays API unavailable and never substitutes a healthy result.
5. **6e — Provider credentials absent:** development, tests, builds, linting, and preflight complete without a paid-provider call.

### 7. Interface elements [locked]

Context: new

Static elements: product title, reviewer-workspace heading, synthetic-demonstration notice.

Dynamic elements: overall readiness, API status, database status, pgvector status, failure guidance.

### 8. Domain model [locked]

Not applicable — this story creates no operational case, product, evidence, actor, or audit entity. Readiness is an ephemeral boundary response and must not become a shared domain abstraction.

### 9. Integrations and boundaries [locked]

- Browser to Next.js workspace — perennial, direction: both.
- Next.js workspace to FastAPI health boundary — perennial, direction: both.
- FastAPI to PostgreSQL — perennial, direction: both.
- Root development command to rootless Podman — ethereal, direction: both.
- Application to paid providers — ethereal, direction: out, permitted calls: 0.

### 10. Background processes [locked]

Not applicable — `make dev` owns foreground local development processes. This story adds no event worker, scheduler, queue, or detached application job.

### 11. Notifications [locked]

- In-page status — recipient: reviewer — trigger: workspace load or readiness refresh.
- Terminal error — recipient: developer-operator — trigger: runtime mismatch or startup failure.

### 12. Audit and logging [locked]

This story emits ordinary operational logs, not immutable case audit events. Each health request log includes UTC timestamp, service, route, status code, and duration. Responses and logs exclude database URLs, credentials, environment values, stack traces, and synthetic intake content.

### 13. Solution variabilities [locked]

- API base URL — source: config — local default points to the host FastAPI service; no silent fallback value after a failed request.
- Web port — source: config — local default is 3000.
- API port — source: config — local default is 8000.
- Database port — source: config — local default is 5432.
- Runtime versions — source: config — exact values come from `.python-version`, `.nvmrc`, and package metadata.
- Container engine version — source: config — require rootless Podman 5.7.0 or newer and reject older versions before startup.

### 14. Quality attributes *NFR* [locked]

- Local readiness endpoint p95 latency: less than 1 second over 20 sequential checks.
- Workspace readiness display p95 latency: less than 1 second after the API response over 20 sequential checks.
- Readiness false-positive tolerance when PostgreSQL or pgvector is unavailable: 0.
- Paid-provider calls during ordinary gates: 0.
- Supported local concurrency for this story: 1 developer-operator and 1 browser session.

### 15. Security and compliance *NFR* [locked]

- AuthN: not applicable to liveness and readiness in this story; attributable local identity arrives in e01s02.
- AuthZ: health boundaries expose status only and no operational records.
- Data classification: local operational metadata with no medical or personal data.
- Controls: no credentials, connection strings, environment values, or stack traces in health responses or workspace output.
- Data policy: fictional and synthetic content only.
- Claims: no compliance, clinical-validation, regulatory-validation, or production-suitability claim.

### 16. UX and accessibility *NFR* [locked]

- Accessibility target: WCAG 2.2 AA checks for semantic status text, color-independent state, keyboard reading order, and visible focus.
- Language scope: English only.
- Supported modality: desktop browser text interface.
- Status labels use text in addition to color.
- Branding remains restrained and must include a synthetic-demonstration notice.

### 17. Acceptance criteria [locked]

Scenario: Healthy local workspace
  Given Python 3.14.6, Node.js 24.18.1, and rootless Podman 5.7.0 or newer are available
  And PostgreSQL 18 starts with pgvector 0.8.6
  When the developer-operator starts the workspace with make dev
  Then API liveness returns HTTP 200
  And API readiness returns HTTP 200
  And the workspace shows API, database, and pgvector as ready

Scenario: Runtime mismatch (6a)
  Given the active Python or Node.js version does not match the pinned version
  When the developer-operator starts or verifies the workspace
  Then the command exits non-zero before application startup
  And the output names the required and detected versions

Scenario: Database unavailable (6b)
  Given the FastAPI process is running
  And PostgreSQL is unavailable
  When readiness is requested
  Then liveness returns HTTP 200
  And readiness returns HTTP 503
  And the workspace does not show ready

Scenario: pgvector unavailable (6c)
  Given PostgreSQL accepts connections
  And the vector extension is absent
  When readiness is requested
  Then readiness returns HTTP 503
  And the workspace shows pgvector as unavailable

Scenario: API unavailable (6d)
  Given the Next.js workspace is running
  And FastAPI is unavailable
  When the reviewer opens the workspace
  Then the workspace shows API unavailable
  And no API, database, or pgvector state is reported as ready

Scenario: Deterministic gates without provider credentials (6e)
  Given no paid-provider credential is configured
  When the developer-operator runs make test, make build, make lint, and make preflight
  Then every gate can complete without a paid-provider request
  And no gate reports an automated check as passed unless it ran

### 18. Out of scope [locked]

- This story does not create local actors, sessions, roles, or permission enforcement; e01s02 owns those capabilities.
- This story does not create cases, protected originals, sanitized revisions, evidence, drafts, approvals, or audit events.
- This story does not add AI, embeddings, MCP, LangGraph, public connectors, or provider credentials.
- This story does not provide production deployment, durable workers, cloud services, OIDC, or public access.
- This story does not add a general observability backend or production uptime claim.

### 19. Open questions [locked]

Not applicable — the local topology, package managers, lint tools, readiness behavior, and success contract are confirmed.

### 20. References [locked]

- `specs/product/SCOPE_LATEST.yaml` — IS-01 and v0.1 constraints.
- `specs/tech-architecture/tech-stack.md` — validated runtime, framework, and database baseline.
- `specs/epics/e01-executable-local-foundation/epic.yaml` — parent epic and dependencies.
- `specs/planning-context.yaml` — synthetic-only, timing, and root-command constraints.
- `AGENTS.md` — project safety and workflow rules.
- <https://nextjs.org/blog/next-16> — Next.js 16 runtime baseline.
- <https://github.com/pgvector/pgvector#docker> — versioned PostgreSQL/pgvector OCI image and extension setup.
- <https://docs.podman.io/en/stable/markdown/podman.1.html> — daemonless and rootless Podman behavior.
- <https://docs.podman.io/en/stable/markdown/podman-compose.1.html> — external Compose provider behavior intentionally avoided here.

## Requirement deltas [locked]

#### ADDED: R-e01s01-01 Exact local runtime contract

The repository must require Python 3.14.6 and Node.js 24.18.1 and must fail clearly before startup when either runtime differs.

#### MODIFIED: R-e01s01-02 One-command hybrid development topology

**Before:** `make dev` runs Next.js and FastAPI on the host and PostgreSQL/pgvector through Docker Compose.

**After:** `make dev` runs Next.js and FastAPI on the host and the pinned PostgreSQL/pgvector OCI image through direct rootless Podman commands, without Compose or a Docker fallback.

#### ADDED: R-e01s01-03 Independent liveness and dependency readiness

FastAPI liveness must remain independent from PostgreSQL. FastAPI readiness must succeed only when PostgreSQL is reachable and pgvector exists.

#### ADDED: R-e01s01-04 Truthful reviewer status

The reviewer workspace must display API, database, and pgvector readiness and must never convert an unavailable dependency into a ready state.

#### ADDED: R-e01s01-05 Deterministic root gates

`make test`, `make build`, `make lint`, and `make preflight` must be runnable, deterministic, and free of paid-provider calls.

## Implementation steps [locked]

1. Establish the pinned runtime files, `uv` and `npm` lock roots, root command harness, and contract tests without introducing application behavior → verify: `make test`
2. Add the rootless Podman lifecycle for the pinned PostgreSQL/pgvector OCI image and FastAPI liveness/readiness behavior, including database and extension failure tests and no new security findings in affected paths → verify: `make test`
3. Add the minimal Next.js reviewer workspace and Playwright checks for ready, API-unavailable, database-unavailable, and pgvector-unavailable states → verify: `make test`
4. Add host-process development orchestration with runtime checks, startup failure propagation, and cleanup behavior without adding a general process-management framework → verify: `make build`
5. Complete Ruff, ESLint, lockfile, runtime, deterministic-test, and no-paid-provider gates and confirm no new security findings in affected paths → verify: `make preflight`

## Verification Script (Step-by-Step) [locked]

1. Activate Node.js 24.18.1, ensure `uv` can resolve Python 3.14.6, and confirm rootless Podman 5.7.0 or newer is available.
2. Run `make preflight` and confirm every root gate succeeds without provider credentials.
3. Run `make dev` and wait for the workspace URL.
4. Open the workspace and confirm the synthetic-demonstration notice and all ready states.
5. Request API liveness and readiness and confirm both return HTTP 200.
6. Stop the rootless Podman PostgreSQL container and confirm liveness remains HTTP 200 while readiness returns HTTP 503.
7. Refresh the workspace and confirm it no longer reports ready.
8. Restart PostgreSQL, remove or disable pgvector in the isolated test database, and confirm readiness remains HTTP 503.
9. Stop FastAPI and confirm the workspace reports API unavailable without false dependency success.
10. Stop the development command and confirm host child processes terminate cleanly.

## Risks [locked]

- Host runtime drift can make the one-command experience unreliable. Detect Python and Node.js exactly and enforce the minimum Podman version before startup.
- Rootless storage or port behavior can vary by host configuration. Use a Podman-managed named volume, publish only the configured local port, and verify both on Kubuntu 26.04 LTS.
- Health endpoints can leak infrastructure details. Return bounded status identifiers and test that secrets and stack traces are absent.
- A readiness check can become a false-positive cache. Fetch current dependency state and test failure transitions.
- Cross-platform process cleanup can expand the story. Support the documented Linux development environment first and avoid a general supervisor.
- Playwright can become flaky if readiness is time-based. Wait on explicit states and use bounded deterministic fixtures.

## Zoom-out check [locked]

This is a greenfield story and modifies no existing application module. Its purpose is to establish the executable web, API, and database boundaries. Its callers are later reviewer workflows, root development commands, and verification gates. Its contracts are exact runtimes, truthful health semantics, deterministic root commands, and zero paid-provider calls.

## Reason for Depth [locked]

A single development orchestration script is justified because one root command must start and clean up two host processes and one containerized dependency; no reusable process framework is introduced.

## Slopcheck [locked]

- `[OK]` uv and npm — narrow package and lockfile managers selected by the user.
- `[OK]` rootless Podman — direct lifecycle for one local PostgreSQL/pgvector OCI container; no Compose provider or daemon socket.
- `[OK]` FastAPI, Pydantic, psycopg, and Uvicorn — bounded API and readiness stack.
- `[OK]` Next.js 16, React, and TypeScript — locked reviewer-interface stack.
- `[OK]` PostgreSQL 18 and pgvector 0.8.6 — validated transactional and vector baseline.
- `[OK]` pytest and Playwright — locked backend and browser verification tools.
- `[OK]` Ruff and ESLint — user-selected lint tools with narrow responsibilities.
- No `[SUS]` or `[SLOP]` dependency is proposed.

## Red-flag check [locked]

The plan avoids four rationalizations: running every process in containers despite the chosen hybrid topology, adding an external Compose provider for one container, retaining an unrequested Docker fallback, and adding authentication before e01s02. It also avoids a general shared utility or process supervisor for one local command.
