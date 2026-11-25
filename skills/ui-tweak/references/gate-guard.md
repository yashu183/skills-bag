# Optional: enforce the approval gate with a hook

This hook is **Claude Code only** (it uses Claude Code's `PreToolUse` hook API and `settings.json`). In other agents, skip it: the gate relies on the instructions in `SKILL.md`.

A skill is instructions; the model usually follows them, but nothing *forces* it. If the user wants a hard guarantee that app source isn't edited while a mock is under review, install the PreToolUse hook in `scripts/ui-tweak-guard.sh`.

How it works:
- While `.ui-tweak/pending` exists in the project root, any `Edit`, `Write` or `MultiEdit` to a path **outside** `.ui-tweak/` is blocked, with a message telling the model to finish the review first.
- Phase 4 of the skill deletes `pending`, which lifts the block.
- With no `pending` file, the hook does nothing. It costs nothing on non-UI work.

Limits: it doesn't see shell commands (`sed -i`, `cat >`), so a determined model could still bypass it via Bash. It's a guard rail, not a sandbox.

## Install (only when the user asks for it)

1. Copy the script somewhere stable and make it executable, e.g. `~/.claude/hooks/ui-tweak-guard.sh` (user-wide) or `.claude/hooks/ui-tweak-guard.sh` (one project).
2. Add it to `settings.json` (user: `~/.claude/settings.json`; project: `.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/ui-tweak-guard.sh" }
        ]
      }
    ]
  }
}
```

Merge into any existing `hooks` block rather than replacing it. It requires `python3` on PATH.

## Escape hatch

If the user wants to override mid-review ("just edit it"), delete `.ui-tweak/pending`.
