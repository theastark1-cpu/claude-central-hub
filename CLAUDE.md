# Instructions for Claude Code Agents

You are working in a shared repo used by two Claude Code agents: **Thea** and **Amber**.

## Before Starting Any Work
1. Run `git pull` to get the latest changes.
2. Check `shared/tasks/BOARD.md` to see what's in progress.
3. Check `shared/decisions/LOG.md` for recent decisions.

## While Working
- Log decisions in `shared/decisions/LOG.md`.
- Update `shared/tasks/BOARD.md` when you start or finish a task.
- Use your own `agents/<your-name>/` folder for scratch work.
- Don't modify the other agent's folder.

## When Done
1. Commit with a clear message: `[Thea] did X` or `[Amber] did Y`.
2. Push immediately so the other agent can see your changes.

## Conflict Resolution
- Resolve conservatively — don't delete the other agent's work.
- When in doubt, leave a note and flag it for the human.
