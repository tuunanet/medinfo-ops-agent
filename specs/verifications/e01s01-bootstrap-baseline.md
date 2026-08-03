# e01s01 Bootstrap Baseline

- Status: Approved one-time exception
- Approved by: Project owner
- Approved at: 2026-08-02T14:44:09Z
- Applies to: Creating `feat/e01s01-local-workspace` only
- Expires: When e01s01t01 makes the root verification harness runnable

## Reason

The `kickoff-branch` gate normally requires `make preflight` on `main`. The approved e01s01 story owns the initial Makefile and root verification harness, so that command cannot exist before its implementation branch exists.

The project owner approved the planning baseline as the one-time substitute for branch creation. This exception does not mark application tests, builds, lint, or runtime checks as passed.

## Substitute evidence

Before branch creation, the project passed:

- parsing of every specification YAML file;
- the bigpowers YAML validator;
- the e01 capsule consistency gate with zero findings;
- Agentic STE validation;
- release-index and task-ledger semantic checks;
- staged whitespace, secret-pattern, prohibited-data, and unsupported-claim checks;
- local-to-remote commit verification on protected public `main`.

The baseline commit was `e4fca64ba4cf3c02d0bda41a1b266c100f30e533`.

## Constraints

- e01s01t01 must create the root command contract before later story tasks proceed.
- `make preflight` must pass after it becomes available and at every later integration gate.
- No future story or branch may reuse this exception.
