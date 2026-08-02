# medinfo-ops-agent — AI Agents

Read `CONVENTIONS.md` before any GitHub or Git operation.

<!-- BEGIN bigpowers:project -->
## Project

Build an auditable, human-controlled medical-information workflow using AI for synthetic triage, retrieval, and cited drafting.

All operational products, requests, evidence, actors, and recipients MUST remain fictional.

## Stack

- Use Python 3.14.6 with FastAPI, Pydantic, LangGraph, and FastMCP.
- Use Node.js 24.18.1 LTS with Next.js, React, and TypeScript.
- Use PostgreSQL with pgvector for transactional and retrieval persistence.
- Keep model, embedding, authentication, storage, and integration providers replaceable.

## Commands

| Action | Command |
|--------|---------|
| Run | `make dev` |
| Test | `make test` |
| Build | `make build` |
| Lint | `make lint` |
| Preflight | `make preflight` |
| CI | `gh pr checks` when a PR exists |

## Architecture

Organize the monorepo around a Next.js interface, FastAPI application, domain modules, LangGraph workflows, and typed adapters.

Persist transactional, workflow, audit, and retrieval data in PostgreSQL and pgvector.

## Conventions

- Organize backend code by domain capability.
- Keep domain rules independent from frameworks and providers.
- Use typed schemas at every trust boundary.
- Keep revisions, approvals, evidence snapshots, and audit events immutable.
- Use `snake_case` in Python.
- Use `camelCase` and `PascalCase` in TypeScript.
- Use UTC internally.
- Give opaque identifiers explicit `*_id` names.
- Avoid shared utility modules without clear ownership.

## Never

- NEVER use real medical, personal, customer, or pharmaceutical case data.
- NEVER send raw intake to models, embeddings, tools, logs, or traces.
- NEVER let AI approve, release, suppress findings, or select destinations.
- NEVER bypass backend authorization, authorship, or evidence checks.
- NEVER use ineligible or live-demo evidence operationally.
- NEVER commit secrets, credentials, local environment files, or protected artifacts.
- NEVER make paid provider calls from ordinary tests.
- NEVER tune against frozen holdouts or alter gold labels for passing metrics.
- NEVER work directly on `main` outside the solo-local landing workflow.
- NEVER claim unimplemented capabilities, compliance, clinical validation, or real-world suitability.

## Agent Rules

- You MUST use bigpowers skills for feature and bug work.
- DO NOT write implementation code before approved specs and runnable verification tasks exist.
- Read `specs/` before writing code.
- Write all planning output under `specs/`.
- Write the minimum code that satisfies the active story.
- Run relevant tests after every change.
- Run Preflight before forward work or integration.
- Fix or log every reproducible gate failure.
- Show verification evidence before declaring work complete.
- Ask one clarifying question instead of encoding an unresolved assumption.

## Tool Wiring

| Tool | Project-local wiring |
|------|----------------------|
| Pi coding agent | Loads root `AGENTS.md`; trusted `.pi/prompts/solo-git.md` registers `/solo-git`. |
| Cline | Reads root `AGENTS.md` natively. |
| Codex CLI | Reads `AGENTS.md` through `.codex/config.toml`. |
| Claude Code | Reads the `CLAUDE.md` symlink to `AGENTS.md`. |
<!-- END bigpowers:project -->

<!-- BEGIN bigpowers:context-routing -->
## Context Routing

| Glob | Additional context |
|------|--------------------|
| `**/*` | Use this root `AGENTS.md`. |
| `apps/web/**` | Add `apps/web/AGENTS.md` when web-specific rules become necessary. |
| `services/api/**` | Add `services/api/AGENTS.md` when API-specific rules become necessary. |
| `packages/**` | Add package-level context only for materially different module rules. |
| `mcp/**` | Add MCP-specific context before implementing live or synthetic tool servers. |
<!-- END bigpowers:context-routing -->

<!-- BEGIN bigpowers:learned-preferences -->
## Learned User Preferences

- None recorded yet.

## Workspace Facts

- None recorded yet.
<!-- END bigpowers:learned-preferences -->

<!-- BEGIN bigpowers:workflow-recipes -->
## Workflow Recipes

| Command | Recipe | Purpose |
|---------|--------|---------|
| `/solo-git` | `specs/workflows/solo-git.yaml` | Deliver one approved story through the complete guarded solo-local lifecycle. |

Treat recipe commands as workflow mappings, not automatic permission to bypass skill gates.
<!-- END bigpowers:workflow-recipes -->
