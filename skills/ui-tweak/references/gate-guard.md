# Optional guard hook

A skill is instructions; the model usually follows them, but nothing *forces* it. For users who want a hard guarantee that app source isn't edited while a mock is under review, there's an optional hook in `scripts/ui-tweak-guard.sh`. It works in Claude Code only (it uses Claude Code's `PreToolUse` hook API). In other agents, the gate relies on the instructions in `SKILL.md`.

How it works:
- While `.ui-tweak/pending` exists in the project root, any `Edit`, `Write` or `MultiEdit` to a path **outside** `.ui-tweak/` is blocked, with a message telling the model to finish the review first.
- Phase 4 of the skill deletes `pending`, which lifts the block.
- With no `pending` file, the hook does nothing. It costs nothing on non-UI work.

Limits: it doesn't see shell commands (`sed -i`, `cat >`), so a determined model could still bypass it via Bash. It's a guard rail, not a sandbox.

## Install

The user installs it themselves; don't change their agent settings for them. If they ask how, point them to the setup guide: https://github.com/yashu183/skills-bag/blob/main/docs/ui-tweak-guard.md

## Escape hatch and abandoned reviews

Delete `.ui-tweak/pending` (keep the mocks) whenever the review ends without approval: the user wants to override mid-review ("just edit it"), drops the idea, or moves on to unrelated work that needs source edits. A stale `pending` would otherwise block every later edit in the project. See SKILL.md, "When the review ends without approval".

The mocks never need a change to the repo's own `.gitignore`: `.ui-tweak/.gitignore` (containing `*`) keeps the folder out of git, and it's written inside `.ui-tweak/`, so the guard allows it.
