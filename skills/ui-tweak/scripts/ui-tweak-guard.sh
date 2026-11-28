#!/usr/bin/env bash
# PreToolUse hook for the ui-tweak skill.
# While <project>/.ui-tweak/pending exists, block Edit/Write/MultiEdit on any
# file outside <project>/.ui-tweak/. Exit 2 = block, stderr is shown to the model.
set -u

project="${CLAUDE_PROJECT_DIR:-$PWD}"
pending="$project/.ui-tweak/pending"

[ -f "$pending" ] || exit 0

target="$(python3 -c 'import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
print((d.get("tool_input") or {}).get("file_path", ""))' 2>/dev/null)"

[ -n "$target" ] || exit 0

# Resolve to an absolute, normalised path.
abs="$(python3 -c 'import os,sys; print(os.path.realpath(os.path.join(sys.argv[1], sys.argv[2])))' "$project" "$target")"
mockdir="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$project/.ui-tweak")"

case "$abs" in
  "$mockdir"/*) exit 0 ;;
esac

slug="$(head -n1 "$pending" 2>/dev/null)"
echo "ui-tweak: a UI mock ('${slug}') is still under review, so app source edits are blocked. Keep changes in .ui-tweak/ until the user says 'implement'; then delete .ui-tweak/pending and edit the source. If the user has dropped this review or asked for unrelated work, delete .ui-tweak/pending first, tell them the review is closed, then make the edit." >&2
exit 2
