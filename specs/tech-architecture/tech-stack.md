# Technology Stack

Status: documentation-validated v0.2 baseline as of 1 August 2026.

## Locked application baseline

| Area | v0.2 baseline | Policy |
| --- | --- | --- |
| Backend runtime | Python 3.14.6 | Run a day-zero runtime smoke test before feature implementation. |
| Backend framework | FastAPI and Pydantic | Resolve and lock exact stable versions. |
| Persistence mapping | SQLAlchemy 2 and Alembic | Keep ORM mappings separate from Pydantic schemas and domain types. Use versioned reviewed migrations. |
| Orchestration | LangGraph with PostgreSQL checkpointing | Use stable thread IDs and replay-safe nodes. |
| MCP | Standalone FastMCP 3.4.5 | Use the stable 3.x line and in-memory transport for v0.2. |
| Frontend runtime | Node.js 24.18.1 LTS | Do not develop against the locally active Node.js 26 runtime. |
| Frontend framework | Next.js 16 App Router, React, and TypeScript | Resolve and lock exact stable versions. Do not use canary packages. |
| Database | PostgreSQL 18 with pgvector 0.8.6 | Use the versioned `0.8.6-pg18-trixie` development and CI image. |
| Local container runtime | Rootless Podman 5.7.0 or newer | Run the single database OCI container through direct Podman commands. Do not add Compose, Docker fallback, privileged mode, or a network API socket. |
| Tests | pytest and Playwright | Ordinary tests use deterministic providers and make no paid calls. |

Python dependency resolution succeeded for 99 packages on local CPython 3.14.4. This result proves resolver compatibility only. The install, import, database, checkpoint, and MCP smoke test must pass on Python 3.14.6.

## OpenAI boundary

- Use replaceable model and embedding adapters over the Responses and Embeddings APIs.
- Use `gpt-5.6-luna` by default.
- Permit `gpt-5.6-terra` only through explicit configuration for bounded evaluation or manually initiated escalation.
- Never use Terra as a silent fallback.
- Use `text-embedding-3-small` with 1,536 dimensions and `vector(1536)` storage.
- Set `store=false` on every Responses request.
- Do not use Conversations, background mode, built-in web search, or remote MCP.
- Accept standard abuse-monitoring retention of up to 30 days only for minimized, sanitized, synthetic content, and disclose it.
- Use simple strict Structured Outputs schemas with `additionalProperties: false`.
- Treat refusal, incomplete output, timeout, and parse failure as typed non-success outcomes. Permit at most one bounded retry before manual handling.
- Treat Luna and Terra names as mutable aliases. Record the requested alias, returned model identifier, inputs, outputs, configuration, and timestamps for every real-provider evaluation.
- Do not claim exact provider reproducibility.
- Require paid project access to pass a smoke test by 3 August 2026. If it fails, continue with deterministic adapters and do not describe v0.2 as real-provider complete.
- Enforce the USD 30 development allowance and explicit per-run token limits.

## LangGraph and domain boundary

- Use a PostgreSQL checkpointer in a schema separate from authoritative domain records.
- Supply a stable `thread_id` for every graph invocation.
- Use interrupts for reviewer feedback and revision only.
- Keep approval and release as separately authorized backend domain commands.
- Treat checkpoints as non-authoritative execution state.
- Keep case revisions, evidence snapshots, approvals, release records, and audit events in domain-owned immutable records.
- Use stable operation identifiers and idempotent domain commands for graph side effects.
- Keep nodes deterministic and replay-safe around interrupts.
- Run v0.2 AI workflows synchronously through explicit user actions with bounded timeouts, cancellation, checkpointed progress, and manual retry.
- Make no durable asynchronous-execution claim for v0.2.

## MCP boundary

- Pin `fastmcp==3.4.5`; its stable dependency line uses MCP SDK 1.x rather than the current MCP SDK 2.x line.
- Do not claim support for FastMCP 4 or the latest MCP protocol features in v0.2.
- Keep each MCP server in an independently owned module with typed tools and an explicit client contract.
- Use in-memory client transport for local v0.2 operation.
- Let LangGraph select and invoke allowlisted read-only tools deterministically.
- Permit a model to propose a typed search query only. Do not permit it to select arbitrary tools, call counts, providers, or destinations.
- Move live or higher-trust connectors to authenticated HTTP services only after a later architecture decision.

## Retrieval boundary

- Apply product, language, jurisdiction, lifecycle, version, and evidence-tier eligibility before ranking.
- Use exact pgvector cosine search for the small v0.2 corpus.
- Combine vector results with PostgreSQL full-text results by deterministic reciprocal-rank fusion.
- Do not add HNSW or IVFFlat until a benchmark demonstrates a latency need and validates recall after filtering.
- Record model alias, dimensions, source-content hash, sanitizer version, and creation time for each immutable embedding revision.

## Deferred architecture decisions

A durable worker and queue, cloud host, OIDC provider, observability backend, object storage, cache, and secrets manager remain open for later releases. Record each selected option in `specs/adr/` before implementation depends on it.

## Official documentation evidence

- OpenAI model capabilities and pricing: <https://developers.openai.com/api/docs/models/gpt-5.6-luna> and <https://developers.openai.com/api/docs/models/gpt-5.6-terra>
- OpenAI Structured Outputs: <https://developers.openai.com/api/docs/guides/structured-outputs>
- OpenAI data controls: <https://developers.openai.com/api/docs/guides/your-data>
- OpenAI embeddings: <https://developers.openai.com/api/docs/guides/embeddings>
- OpenAI function control: <https://developers.openai.com/api/docs/guides/function-calling#tool-choice>
- LangGraph persistence: <https://docs.langchain.com/oss/python/langgraph/persistence>
- LangGraph interrupts: <https://docs.langchain.com/oss/python/langgraph/interrupts>
- LangGraph durable execution: <https://docs.langchain.com/oss/python/langgraph/durable-execution>
- FastMCP installation and versioning: <https://gofastmcp.com/getting-started/installation>
- FastMCP transports: <https://gofastmcp.com/clients/client>
- Next.js 16: <https://nextjs.org/blog/next-16>
- pgvector search, filtering, and OCI image versions: <https://github.com/pgvector/pgvector>
- Podman daemonless and rootless operation: <https://docs.podman.io/en/stable/markdown/podman.1.html>
- Podman Compose provider behavior: <https://docs.podman.io/en/stable/markdown/podman-compose.1.html>
- Podman installation on Ubuntu: <https://podman.io/docs/installation>
- FastAPI background-task limits: <https://fastapi.tiangolo.com/tutorial/background-tasks/#caveat>
- SQLAlchemy 2 typed mappings: <https://docs.sqlalchemy.org/en/20/orm/quickstart.html>
- Alembic migrations: <https://alembic.sqlalchemy.org/en/latest/tutorial.html>
- Starlette signed sessions: <https://www.starlette.io/middleware/#sessionmiddleware>
- Next.js same-origin rewrites: <https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites>
