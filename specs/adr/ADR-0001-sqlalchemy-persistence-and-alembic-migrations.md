# ADR-0001: Use SQLAlchemy 2 mappings and Alembic migrations

- Status: Accepted
- Date: 2026-08-02
- Decision owner: Project owner
- Applies from: e01s02

## Context

The application needs persistent actors, permission bundles, immutable revisions, evidence snapshots, approvals, releases, audit events, and vector-backed evidence. These records require explicit PostgreSQL constraints and controlled schema evolution.

Pydantic owns validation at trust boundaries. Domain rules must remain independent from web frameworks and persistence providers. A persistence model must therefore not also become the API schema or the authoritative domain model.

SQLModel was considered because it reduces duplication by combining Pydantic and SQLAlchemy behavior. That overlap conflicts with the deliberate separation required here.

## Decision

Use SQLAlchemy 2 typed declarative mappings for PostgreSQL persistence and Alembic for versioned schema migrations.

Apply these boundaries:

- Domain entities and rules do not inherit from SQLAlchemy or Pydantic classes.
- Pydantic request and response schemas remain trust-boundary types.
- SQLAlchemy mapped classes remain inside persistence adapters.
- Capability-owned repositories translate between persistence records and domain values.
- Do not create a generic repository or shared unit-of-work abstraction without a concrete cross-capability need.
- Use explicit database constraints for identity, relationship, lifecycle, and immutability invariants where PostgreSQL can enforce them.
- Alembic migrations are the only supported path for application-schema changes.
- Review generated migrations before execution; autogeneration is an aid, not approval.
- Keep PostgreSQL and pgvector details replaceable behind typed capability boundaries without pretending that all databases provide equivalent behavior.

## Consequences

### Positive

- API, domain, and persistence representations have explicit ownership.
- Complex PostgreSQL constraints and relationships remain available without an abstraction ceiling.
- Alembic provides an established, reviewable migration history.
- Later pgvector and immutable-record work can use native SQLAlchemy and PostgreSQL features.

### Negative

- Mapping between Pydantic, domain, and persistence types requires deliberate code.
- SQLAlchemy and Alembic add concepts and configuration beyond direct psycopg queries.
- Small CRUD paths contain more boilerplate than equivalent SQLModel paths.

## Alternatives

### SQLModel with Alembic

Rejected for this release. Its reduced duplication is valuable for simple CRUD, but it encourages API and table representations to share one model hierarchy.

### psycopg with plain SQL migrations

Rejected for this release. It minimizes dependencies but creates project-owned migration tooling and more repetitive relationship mapping.

## References

- <https://docs.sqlalchemy.org/en/20/orm/quickstart.html>
- <https://alembic.sqlalchemy.org/en/latest/tutorial.html>
- <https://sqlmodel.tiangolo.com/>
- `AGENTS.md`
- `specs/tech-architecture/tech-stack.md`
