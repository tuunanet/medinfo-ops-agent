---
description: Resume the guarded solo-local story lifecycle
---
Read `specs/workflows/solo-git.yaml` and `specs/state.yaml`.

Resume the first eligible incomplete recipe step.

Respect every recipe gate and human checkpoint.

Stop after one skill reaches `success`, `no-op`, `blocked`, or `exhausted`.

Record the terminal state in `specs/state.yaml` under `handoff.last_terminal_state`.

Never bypass worktree, Preflight, evaluation, UAT, audit, or release gates.
