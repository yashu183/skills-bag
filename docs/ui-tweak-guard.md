# ui-tweak guard hook (optional, Claude Code only)

Without the hook, "don't edit code before approval" is an instruction the agent usually follows. With it, Claude Code blocks the edit.

It uses Claude Code's `PreToolUse` hook API, so other agents ignore it. In those agents, the approval gate relies on the skill's instructions alone.

## How it works

- While `<project>/.ui-tweak/pending` exists, any `Edit`, `Write` or `MultiEdit` to a path **outside** `.ui-tweak/` is blocked, with a message telling the agent to finish the review first.
- Phase 4 of the skill (implement) deletes `pending`, which lifts the block.
- With no `pending` file, the hook does nothing, so it costs nothing on other work.
- It doesn't see shell commands (`sed -i`, `cat >`), so it's a guard rail, not a sandbox.

## Install

The script ships with the skill at `scripts/ui-tweak-guard.sh` and needs `python3` on your PATH.

1. Make sure it's executable:

   ```bash
   chmod +x ~/.claude/skills/ui-tweak/scripts/ui-tweak-guard.sh
   ```

2. Add this to `~/.claude/settings.json` (every project) or `<project>/.claude/settings.json` (one project), merging into any existing `hooks` block rather than replacing it:

   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Edit|Write|MultiEdit",
           "hooks": [
             { "type": "command", "command": "~/.claude/skills/ui-tweak/scripts/ui-tweak-guard.sh" }
           ]
         }
       ]
     }
   }
   ```

   If you installed the skill somewhere else, use that path in `command`.

## Override mid-review

Delete `.ui-tweak/pending`.

## Remove

Delete the hook entry from `settings.json`.
