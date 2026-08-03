# ADR-0002: Use rootless Podman for the local database

- Status: Accepted
- Date: 2026-08-02
- Decision owner: Project owner
- Applies from: e01s01

## Context

The hybrid local topology runs Next.js and FastAPI on pinned host runtimes and needs one containerized PostgreSQL 18 service with pgvector 0.8.6. The target development host is Kubuntu 26.04 LTS.

Docker Compose was selected during initial planning but was not installed when implementation started. The project owner prefers Podman for native Linux development.

Podman supports daemonless, rootless container execution and a Docker-comparable CLI. Its `podman compose` command delegates to an external Compose provider. One database container does not justify that extra provider.

## Decision

Use direct rootless Podman commands for the local PostgreSQL and pgvector lifecycle.

Apply these constraints:

- Require Podman 5.7.0 or newer.
- Run as the development user without `sudo` or privileged mode.
- Use `docker.io/pgvector/pgvector:0.8.6-pg18-trixie` as the fully qualified OCI image.
- Use a Podman-managed named volume for PostgreSQL data.
- Publish only the configured loopback database port.
- Use one explicit project-owned container name.
- Stop the container during development cleanup and preserve the named volume.
- Do not use `podman compose`, `docker-compose`, a Docker fallback, or a network API socket.
- Keep the container lifecycle behind one project-owned development script. Do not create a general container abstraction.
- Test lifecycle command generation with a deterministic fake executable and keep the real rootless-container smoke test explicit.

## Consequences

### Positive

- Local database execution is daemonless and rootless.
- The project needs one container engine and no Compose provider.
- The pinned pgvector OCI image remains unchanged.
- The application continues to connect through an ordinary PostgreSQL boundary and does not depend on Podman APIs.

### Negative

- Developers must install Podman 5.7.0 or newer.
- Docker-only environments are not supported by the v0.2 local workflow.
- Rootless storage, port, and user-namespace behavior require target-host verification.
- CI environments that do not offer Podman need a later explicit runtime decision.

## Alternatives

### Docker Compose

Rejected for local v0.2 development. It adds a daemon and Compose dependency that the selected Kubuntu host does not need for one container.

### podman compose

Rejected. Podman documents this command as a wrapper around an external Compose provider.

### Support Docker and Podman

Rejected. A dual-runtime abstraction adds configuration and test combinations without improving the deadline path.

### Install PostgreSQL directly on the host

Rejected. It weakens version isolation and makes pgvector lifecycle and cleanup less reproducible.

## Validation

Record cold-start and readiness measurements on the target host. Do not claim a performance improvement over Docker without a controlled comparison.

## References

- <https://docs.podman.io/en/stable/markdown/podman.1.html>
- <https://docs.podman.io/en/stable/markdown/podman-compose.1.html>
- <https://podman.io/docs/installation>
- <https://github.com/pgvector/pgvector#docker>
- `specs/tech-architecture/IMPACT_LATEST.md`
- `specs/epics/e01-executable-local-foundation/e01s01-open-local-workspace.md`
