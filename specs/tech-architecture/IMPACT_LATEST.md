# Impact Assessment: Replace Docker Compose with rootless Podman

- Status: Accepted
- Date: 2026-08-02
- Target: e01s01 local PostgreSQL and pgvector container lifecycle

## Proposed change

Replace Docker Compose with rootless Podman on the documented Kubuntu 26.04 LTS development host. Use the Podman CLI directly for the single PostgreSQL/pgvector container rather than `podman compose`.

Use the fully qualified OCI image `docker.io/pgvector/pgvector:0.8.6-pg18-trixie`, a Podman-managed named volume, an explicit local port, and an application-owned lifecycle script. Do not start a Podman API socket, use a network API, require rootful containers, or install an external Compose provider.

## Dependents (8)

1. `specs/state.yaml` — selected local topology and environment blocker.
2. `specs/tech-architecture/tech-stack.md` — local container-runtime baseline and pgvector reference wording.
3. `specs/epics/e01-executable-local-foundation/e01s01-open-local-workspace.md` — preconditions, main flow, boundary, acceptance criteria, requirement delta, steps, slopcheck, and red-flag check.
4. `specs/epics/e01-executable-local-foundation/e01s01-tasks.yaml` — development-orchestration task wording.
5. Root command contract planned by e01s01t01 — tool and version checks.
6. Database lifecycle planned by e01s01t02 — image, volume, port, extension initialization, and failure fixtures.
7. Host-process orchestration planned by e01s01t04 — startup, failure propagation, signal handling, and cleanup.
8. Every later story — indirect dependency on the PostgreSQL and pgvector development service established by e01s01.

## Affected stories

- e01s01 — direct requirement modification.
- e01s02 — indirect; its SQLAlchemy migration and actor seeds require the same PostgreSQL service.
- e02s01 through e07s02 — indirect; all transactional, retrieval, checkpoint, and evaluation work inherits the local database lifecycle.

The change does not alter story value, BCP count, epic order, or WSJF score. e01 remains first with WSJF 10.0.

## Test coverage

No implementation tests exist yet.

Required first-line coverage:

- root command contract fails clearly when Podman is absent or below the supported version;
- deterministic fake-CLI tests cover create, start, readiness wait, stop, failure propagation, and idempotent restart;
- commands never use `sudo`, privileged mode, a TCP API socket, or an external Compose provider;
- an opt-in local smoke test runs the pinned pgvector image rootlessly and verifies PostgreSQL 18 plus extension version 0.8.6;
- cleanup stops the container but preserves the named development volume;
- API liveness and readiness behavior remains unchanged when the container is stopped.

## Compatibility evidence

- Podman describes itself as a daemonless container engine with a Docker-comparable CLI, and most commands can run as a regular user.
- Podman is available from the official Ubuntu repositories for Ubuntu 20.10 and newer.
- Kubuntu 26.04 currently offers Podman 5.7.0 through its Ubuntu repository.
- `podman compose` is only a wrapper around an external provider such as `docker-compose` or `podman-compose`; direct CLI use avoids that extra dependency.
- The pgvector project publishes the pinned `0.8.6-pg18-trixie` OCI image tag.

## Risk: High

The mechanical change is small, but the container lifecycle is a shared foundation for every story and currently has no implementation tests. Rootless storage, port publication, signal cleanup, and volume behavior must be proven on the target host.

Numeric risk score: 7/10 — broad downstream dependency, bounded single-container fan-out, and no implementation churn. No grill session is required by the greater-than-7 rule.

## Recommended action

Proceed with the project-owner-approved direct rootless Podman design. Update only the affected e01s01 contracts, add the test requirements above, rerun the capsule gates, and install Podman before implementation resumes.

Do not claim that Podman is faster without a local measurement. Treat daemonless and rootless operation as the selection rationale; report cold-start and readiness measurements separately.

## Sources

- <https://docs.podman.io/en/stable/markdown/podman.1.html>
- <https://docs.podman.io/en/stable/markdown/podman-compose.1.html>
- <https://podman.io/docs/installation>
- <https://github.com/pgvector/pgvector#docker>
