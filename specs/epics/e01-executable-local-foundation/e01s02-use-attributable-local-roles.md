STORY KEY: e01s02
TITLE:     Use attributable local roles
TYPE:      Story
PARENT:    e01
STATUS:    Refined
AUTHOR:    planning-agent   DATE: 2026-08-02
MATURITY:  5
SIZE:      M

### 1. Business narrative [locked]

A local reviewer workspace that cannot identify its user cannot support trustworthy authorship, review, approval, release, or audit history. Shared credentials would make later workflow controls cosmetic because the application could not distinguish who performed an action.

The first release needs attributable identities without spending the deadline on production identity infrastructure. Every selectable identity must be explicitly fictional, every permission decision must occur in the backend, and the interface must state that the mechanism is development-only.

### 2. Value statement [locked]

As a fictional operational user, I want to enter through an attributable local identity, so that the application can enforce my permissions and preserve who performed each action.

### 3. Actors and permissions [locked]

- Coordinator (internal) — enter the reviewer workspace through `workspace:view`; later intake permissions remain deferred.
- Reviewer (internal) — enter the reviewer workspace through `workspace:view`; later case-review permissions remain deferred.
- Approver (internal) — enter the reviewer workspace through `workspace:view`; approval rules remain deferred.
- Auditor (internal) — enter the reviewer workspace through `workspace:view`; audit-record access remains deferred.
- Administrator (internal) — receive `administration:view` only and remain denied from the reviewer workspace.
- Multi-role reviewer-approver (internal) — receive the union of Reviewer and Approver permissions without receiving an authorship bypass.
- Development actor switcher (system) — issue a session only for an active repository-seeded fictional actor.
- FastAPI authorization boundary (system) — resolve the signed session, load current permissions, and enforce the required permission.

### 4. Trigger and preconditions [locked]

Trigger: a user opens the local application without an active development session and selects one fictional actor.

Preconditions:

- e01s01 is implemented and its liveness, readiness, and root-command contracts pass.
- The application runs in explicit development configuration.
- PostgreSQL contains the versioned actor, role, permission, actor-role, and role-permission seed records.
- The development process supplies an ephemeral signing secret that is not committed or logged.
- Browser API requests use the same-origin `/api` proxy path.

### 5. Main flow and business logic [locked]

1. An unauthenticated browser displays a development-only actor switcher and synthetic-identity notice.
2. The browser requests the active fictional actor list through the same-origin API path.
3. The user selects one actor and submits the selection with a valid local Origin.
4. FastAPI verifies development mode, Origin, actor existence, fictional status, and active status.
5. FastAPI issues a signed session cookie containing only the opaque `actor_id` and expiry metadata.
6. On each protected request, FastAPI verifies the cookie and loads current roles and permissions from PostgreSQL.
7. The authorization dependency checks `workspace:view` in the resolved permission set.
8. An allowed user enters the reviewer workspace and sees actor label, role labels, and effective permission codes.
9. A denied user sees an explicit access-denied state without protected workspace content.
10. Sign-out clears the session and returns the browser to the actor switcher.

Interruption point: after step 5; the signed session can resume the flow for up to 8 hours.

### 6. Alternative flows and exceptions [locked]

1. **6a — Non-development configuration:** actor-list and actor-selection endpoints return HTTP 404 and issue no session.
2. **6b — Unknown, inactive, or non-fictional actor:** selection fails closed and issues no session.
3. **6c — Missing, expired, malformed, or tampered cookie:** the protected request returns HTTP 401 and the browser returns to actor selection.
4. **6d — Forged client claims:** role, permission, or actor headers do not alter the server-resolved principal.
5. **6e — Administrator-only actor:** authentication succeeds, `workspace:view` fails, and the workspace returns HTTP 403.
6. **6f — Multi-role actor:** effective permissions are the set union of assigned role permissions, with no workflow-rule or authorship bypass.
7. **6g — Invalid Origin on session mutation:** actor selection and sign-out return HTTP 403 and do not change the cookie.
8. **6h — Sign-out:** the session cookie is cleared and subsequent protected requests return HTTP 401.

### 7. Interface elements [locked]

Context: existing

Static elements: development-authentication label, fictional-identity notice, actor-selection heading, sign-out control.

Dynamic elements: actor choices, current actor, assigned roles, effective permissions, access-denied guidance.

### 8. Domain model [locked]

Domain concepts:

- Actor — an attributable fictional person represented by `actor_id`, display label, fictional flag, and active flag.
- Role — a named permission bundle represented by `role_id` and stable `role_code`.
- Permission — a stable capability code such as `workspace:view` or `administration:view`.
- Principal — the request-scoped actor identity, role codes, and effective permission codes resolved by the backend.

Persistence relationships:

- Actor to Role is many-to-many through ActorRole.
- Role to Permission is many-to-many through RolePermission.
- The signed session stores only `actor_id` and expiry metadata; it does not persist role or permission claims.

SQLAlchemy mappings remain inside the identity persistence adapter. Pydantic schemas represent API inputs and outputs. Domain permission evaluation does not inherit from either representation. See `specs/adr/ADR-0001-sqlalchemy-persistence-and-alembic-migrations.md`.

### 9. Integrations and boundaries [locked]

- Browser to Next.js actor interface — perennial, direction: both.
- Next.js `/api/:path*` rewrite to FastAPI — perennial, direction: both. Next.js documents rewrites as a URL proxy that masks the destination path.
- FastAPI SessionMiddleware — perennial, direction: both. Starlette documents signed session data as readable but not modifiable and always sets the cookie `HttpOnly`.
- FastAPI authorization dependency to identity persistence adapter — perennial, direction: both.
- SQLAlchemy 2 to PostgreSQL — perennial, direction: both.
- Alembic to PostgreSQL schema — ethereal, direction: out.
- Paid providers — ethereal, direction: out, permitted calls: 0.

### 10. Background processes [locked]

Not applicable — session verification and permission resolution occur during explicit HTTP requests. This story adds no worker, scheduler, cleanup job, or external identity callback.

### 11. Notifications [locked]

- In-page identity banner — recipient: current user — trigger: authenticated workspace response.
- In-page access-denied state — recipient: authenticated user — trigger: missing `workspace:view`.
- In-page session-expired state — recipient: prior user — trigger: HTTP 401 from a protected request.

### 12. Audit and logging [locked]

This story emits structured authentication and authorization logs, not immutable case audit events. Records include UTC timestamp, request ID, opaque `actor_id` when resolved, event code, required permission when applicable, and allow or deny result.

Logs exclude session-cookie contents, signing secrets, database credentials, role payloads from the client, and stack traces. Later domain actions must copy the server-resolved `actor_id` into their immutable records rather than rely on historical role membership.

### 13. Solution variabilities [locked]

- Application environment — source: config — actor switching is available only for `development`; every other value returns HTTP 404.
- Development session secret — source: config — generated ephemerally by `make dev`; tests inject a fixed synthetic value.
- Session maximum age — source: config — fixed v0.1 default is 28,800 seconds.
- Cookie secure flag — source: config — false for documented local HTTP development only.
- Cookie SameSite — source: config — fixed to `lax`.
- Allowed web Origin — source: config — exact local Next.js Origin; wildcard is prohibited.

### 14. Quality attributes *NFR* [locked]

- Authentication and permission-check p95 latency: less than 1 second over 20 sequential local requests.
- Development session maximum age: 28,800 seconds.
- Unauthorized protected-workspace false acceptance tolerance: 0.
- Client-forged permission acceptance tolerance: 0.
- Seeded canonical role count: 5.
- Seeded multi-role actor count: at least 1.
- Paid-provider calls during ordinary gates: 0.

### 15. Security and compliance *NFR* [locked]

- AuthN: development-only signed session cookie containing opaque `actor_id` and expiry metadata.
- AuthZ: backend permission evaluation with roles used only as permission bundles.
- Data classification: fictional actor metadata and local security metadata.
- Cookie controls: `HttpOnly`, `SameSite=Lax`, 8-hour maximum age, path `/`; `Secure` remains false only for documented local HTTP.
- Mutation controls: exact Origin validation for actor selection and sign-out.
- Trust controls: client actor, role, and permission headers are ignored; current permissions are loaded server-side for each protected request.
- Environment control: actor switcher routes are absent outside development configuration.
- Secret control: signing secret is ephemeral, uncommitted, and excluded from logs and responses.
- Claims: no production authentication, identity assurance, compliance, or public-access claim.

### 16. UX and accessibility *NFR* [locked]

- Accessibility target: WCAG 2.2 AA checks for labeled controls, keyboard actor selection, focus movement, status text, and error association.
- Language scope: English only.
- Supported modality: desktop browser text interface.
- Actor labels state `Fictional` visibly.
- Development authentication remains visually distinct from a production sign-in experience.

### 17. Acceptance criteria [locked]

Scenario: Enter as an operational fictional actor
  Given the application runs in development configuration
  And an active fictional Reviewer actor has workspace:view
  When the user selects that actor
  Then FastAPI issues a signed HttpOnly SameSite Lax session cookie
  And the reviewer workspace displays the server-resolved actor, roles, and permissions

Scenario: Switcher absent outside development (6a)
  Given the application does not run in development configuration
  When a client requests the actor list or submits an actor selection
  Then the API returns HTTP 404
  And no session cookie is issued

Scenario: Reject ineligible actor (6b)
  Given an actor identifier is unknown, inactive, or not marked fictional
  When a client submits that actor identifier
  Then the selection fails closed
  And no session cookie is issued

Scenario: Reject invalid session (6c)
  Given a session cookie is missing, expired, malformed, or tampered
  When the client requests the reviewer workspace
  Then the API returns HTTP 401
  And the interface returns to actor selection

Scenario: Ignore forged client permissions (6d)
  Given an authenticated actor does not have workspace:view
  When the client adds actor, role, or permission headers claiming workspace:view
  Then the headers do not change the server-resolved principal
  And the API returns HTTP 403

Scenario: Administrator does not inherit workflow access (6e)
  Given an Administrator-only actor has administration:view but not workspace:view
  When that actor requests the reviewer workspace
  Then authentication succeeds
  And authorization returns HTTP 403

Scenario: Multi-role permissions are a set union (6f)
  Given one fictional actor has Reviewer and Approver roles
  When the backend resolves the principal
  Then effective permissions contain the union of both role bundles
  And the principal contains no authorship or self-approval bypass

Scenario: Reject invalid session-mutation Origin (6g)
  Given a request Origin does not equal the configured local web Origin
  When the client selects an actor or signs out
  Then the API returns HTTP 403
  And the existing session state does not change

Scenario: Sign out clears access (6h)
  Given an authenticated operational actor can view the workspace
  When that actor signs out
  Then the session cookie is cleared
  And the next protected request returns HTTP 401

### 18. Out of scope [locked]

- This story does not add passwords, password recovery, OIDC, OAuth, MFA, public accounts, or identity proofing.
- This story does not claim that development actor switching is production authentication.
- This story does not add actor, role, or permission administration screens.
- This story does not implement intake, protected-original, review, approval, release, delivery, or audit-record permissions.
- This story does not implement authorship-history or self-approval rules; it only prevents permission bundles from encoding a bypass.
- This story does not persist browser sessions or add a session-cleanup worker.
- This story does not protect liveness or readiness endpoints; they continue to expose bounded status only.

### 19. Open questions [locked]

Not applicable — authentication experience, persistence approach, cookie boundary, role behavior, and success criteria are confirmed.

### 20. References [locked]

- `specs/product/SCOPE_LATEST.yaml` — IS-01 and permission constraints.
- `specs/planning-context.yaml` — target roles, backend authorization, and administrator restrictions.
- `specs/epics/e01-executable-local-foundation/e01s01-open-local-workspace.md` — existing workspace and health contracts.
- `specs/adr/ADR-0001-sqlalchemy-persistence-and-alembic-migrations.md` — accepted persistence boundary.
- <https://www.starlette.io/middleware/#sessionmiddleware> — signed readable session data, `HttpOnly`, SameSite, expiry, and secure-cookie parameters.
- <https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites> — same-origin URL proxy behavior.
- <https://docs.sqlalchemy.org/en/20/orm/quickstart.html> — SQLAlchemy 2 typed declarative mappings.
- <https://alembic.sqlalchemy.org/en/latest/tutorial.html> — versioned migration environment.

## Requirement deltas [locked]

#### MODIFIED: R-e01s01-04 Truthful reviewer status

**Before:** The local readiness workspace is visible without an application identity and displays API, database, and pgvector status.

**After:** Liveness and readiness endpoints remain unauthenticated and bounded, while the reviewer workspace requires a server-resolved principal with `workspace:view`.

#### ADDED: R-e01s02-01 Development-only fictional actor selection

The local interface must list only active repository-seeded fictional actors and must issue no actor-switching route outside development configuration.

#### ADDED: R-e01s02-02 Signed opaque development session

FastAPI must issue a signed `HttpOnly`, `SameSite=Lax` session containing only opaque `actor_id` and expiry metadata after exact Origin and actor eligibility checks.

#### ADDED: R-e01s02-03 Server-owned permission resolution

FastAPI must load current roles and permissions from PostgreSQL for protected requests and must ignore client-supplied actor, role, and permission claims.

#### ADDED: R-e01s02-04 Administrator separation

An Administrator-only actor must remain denied from the reviewer workspace unless a separate role grants `workspace:view`.

#### ADDED: R-e01s02-05 Multi-role union without workflow bypass

Effective permissions must be the set union of assigned role bundles and must not contain an authorship, approval, release, or other workflow-rule bypass.

#### ADDED: R-e01s02-06 Attributable request context

Protected requests must expose one server-resolved opaque `actor_id` to later domain commands and structured logs without recording cookie contents or secrets.

## Implementation steps [locked]

1. Add ADR-0001, SQLAlchemy 2 persistence mappings, Alembic configuration, a reviewed actor-role-permission migration, and deterministic fictional seeds without coupling ORM classes to Pydantic or domain types; confirm no new security findings in affected paths → verify: `make test`
2. Add development-only actor-list, selection, current-session, and sign-out boundaries with Starlette SessionMiddleware, exact Origin checks, 8-hour expiry, and invalid-cookie tests; confirm no new security findings in affected paths → verify: `make test`
3. Add a request-scoped Principal and permission dependency that resolves database state, ignores forged client claims, supports multi-role union, and denies the Administrator-only actor; confirm no new security findings in affected paths → verify: `make test`
4. Modify the Next.js workspace through the same-origin rewrite to add actor selection, current identity, permission display, denied state, expiry recovery, and sign-out with browser accessibility checks; confirm no new security findings in affected paths → verify: `make test`
5. Add structured authentication and authorization logging, production-disable checks, secret and cookie leak checks, migration verification, and full e01 regression coverage; confirm no new security findings in affected paths → verify: `make preflight`

## Verification Script (Step-by-Step) [locked]

1. Run `make preflight` without paid-provider credentials.
2. Run `make dev` in development configuration and open the local application.
3. Confirm the page shows a development-only fictional actor switcher.
4. Select the fictional Reviewer actor and confirm the workspace shows the server-resolved actor, role, and `workspace:view` permission.
5. Sign out and confirm the workspace becomes inaccessible.
6. Select the Administrator-only actor and confirm authentication succeeds but the reviewer workspace shows access denied.
7. Select the multi-role Reviewer-Approver actor and confirm the role and permission union is visible without a self-approval capability.
8. Tamper with the session cookie and confirm the next protected request returns to actor selection.
9. Submit actor selection from an invalid Origin and confirm HTTP 403 with no session change.
10. Run the API outside development configuration and confirm actor-list and selection routes return HTTP 404.
11. Inspect test-captured logs and responses and confirm no cookie, signing secret, database credential, or client-forged claim appears.
12. Confirm e01s01 liveness and readiness behavior remains unchanged.

## Risks [locked]

- A signed session is readable. Store only opaque `actor_id` and expiry metadata and never put roles or permissions in it.
- Development actor switching can be mistaken for production authentication. Remove its routes outside development and label the interface explicitly.
- Client-controlled claims can bypass authorization if trusted. Resolve all effective permissions from database state on every protected request.
- Role permissions can accidentally encode domain bypasses. Keep authorship and revision rules outside RBAC and defer them to their owning stories.
- Same-origin proxy configuration can hide cookie or Origin errors. Cover Set-Cookie, forwarding, sign-out, and invalid-Origin behavior in browser and API tests.
- Alembic autogeneration can miss semantic intent. Review the initial migration and assert schema constraints in tests.

## Zoom-out check [locked]

Purpose of the existing e01s01 boundary: start the local product and report liveness and dependency readiness truthfully.

Callers: the browser workspace, root development commands, cold-start tests, and every later reviewer workflow.

Contracts to preserve: exact runtime checks, unauthenticated bounded health endpoints, truthful dependency status, deterministic root gates, and zero paid-provider calls.

Before e01s02 implementation modifies e01s01 paths, run `assess-impact` against the implemented workspace, API boundary, and root verification harness.

## Reason for Depth [locked]

A request-scoped Principal and one permission dependency are justified because every later protected backend action needs the same server-owned identity contract; no generic authentication framework or shared repository abstraction is introduced.

## Slopcheck [locked]

- `[OK]` SQLAlchemy 2 — user-selected typed persistence mapping with full PostgreSQL control.
- `[OK]` Alembic — user-selected versioned migration tool built on SQLAlchemy.
- `[OK]` psycopg — validated PostgreSQL driver used beneath SQLAlchemy.
- `[OK]` Starlette SessionMiddleware and its signing dependency — existing FastAPI stack capability with documented signed, `HttpOnly` sessions.
- `[OK]` Next.js rewrites — documented same-origin URL proxy in the locked frontend framework.
- `[OK]` pytest and Playwright — locked API, authorization, cookie, and browser verification tools.
- No `[SUS]` or `[SLOP]` dependency is proposed.

## Red-flag check [locked]

The plan rejects three shortcuts: trusting browser role claims, storing effective permissions in the cookie, and reusing persistence models as API or domain models. It also avoids production identity features, actor administration, and a generic repository layer.
