# Claude Central Hub

Shared repository for **Thea** and **Amber** — two Claude Code assistants working in coordination.

## Structure

- `shared/context/` — Project context, background info, architecture notes
- `shared/decisions/` — Decisions made (so neither agent reverses them)
- `shared/specs/` — Specifications, requirements, designs
- `shared/tasks/` — Task board — who's doing what
- `agents/thea/` — Thea's scratchpad
- `agents/amber/` — Amber's scratchpad
- `docs/` — Final documentation

## Workflow

1. Always `git pull` before starting work
2. Claim tasks in `shared/tasks/BOARD.md`
3. Log decisions in `shared/decisions/LOG.md`
4. Don't edit the other agent's folder
5. Commit often with `[Thea]` or `[Amber]` prefix
