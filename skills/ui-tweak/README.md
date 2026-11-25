# ui-tweak

An agent skill for UI changes: **preview first, code later**.

It uses the open [Agent Skills](https://agentskills.io) format (`SKILL.md` + plain Python scripts), so it works in any coding agent that supports skills: Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI and others. The one exception is the optional [guard hook](#2-the-guard-hook-optional-claude-code-only), which is Claude Code-only.

When you ask for a UI tweak or a redesign, the agent doesn't touch your code. It builds an HTML mock of the screen (your current UI next to the proposed change, using your app's real styles and components), serves it on a live-reload local server, and iterates with you, one version per round of feedback. Your source code changes only when you say **implement**.

```
you ask ─► v1 mock ─► feedback ─► v2 (cp v1 → v2, edit) ─► ... ─► "implement" ─► real code ─► verify
```

## Why

Asking an agent for a UI change usually goes: it edits the code, you look, it's not what you pictured, you ask again, and again. Each round is a full code change and burns tokens. A cheap mock lets you agree on the picture first, then the code is written once.

## What's in the folder

```
ui-tweak/
├── SKILL.md                  the instructions the agent follows (Phases 1–5)
├── README.md                 this file (for humans; the agent doesn't need it)
├── references/
│   ├── mock-fidelity.md      where each stack keeps its styles, component inventory, Tailwind CDN snippets
│   └── gate-guard.md         the optional hook (Claude Code only): what it does, how to install it
├── scripts/
│   ├── serve.py              live-reload preview server for .ui-tweak/ (port 4517+)
│   ├── check_native.py       fails if a mock uses browser-default controls instead of in-app ones
│   └── ui-tweak-guard.sh     optional Claude Code PreToolUse hook: blocks source edits while a mock is under review
├── assets/
│   └── preview-template.html the frame every mock starts from (Current / Proposed panels, viewports, dark mode, notes)
└── evals/                    4 test cases for the skill itself
```

## Requirements

- A coding agent that supports Agent Skills (Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, …)
- `python3` on your PATH (the scripts use only the standard library; nothing to `pip install`)

## Install

### 1. The skill

**With npx** (needs Node.js):

```bash
npx skills add https://github.com/yashu183/skills-bag --skill ui-tweak -g
```

It asks which agents to install for and puts the skill in each one's skills folder. `-g` installs it for every project; leave it out to install into the current project only. To skip the picker, name the agent, e.g. `-a claude-code`.

**Or by hand.** Copy or symlink the `ui-tweak` folder into your agent's skills folder (check its docs for the path). For Claude Code that's `~/.claude/skills/` (every project) or `<project>/.claude/skills/` (one project):

```bash
git clone https://github.com/yashu183/skills-bag.git
mkdir -p ~/.claude/skills

# copy (stays as it is)…
cp -R skills-bag/skills/ui-tweak ~/.claude/skills/
# …or symlink (git pull updates it)
ln -s "$PWD/skills-bag/skills/ui-tweak" ~/.claude/skills/ui-tweak
```

If the scripts lost their executable bit on the way, run `chmod +x <skills-folder>/ui-tweak/scripts/*` (the agent calls them with `python3`, so this only matters for the hook).

Start a new agent session so it picks up the skill. In Claude Code, type `/skills` (it should be listed) or `/ui-tweak`; in other agents, use their skills list or just ask for a UI change.

### 2. The guard hook (optional, Claude Code only)

Without the hook, "don't edit code before approval" is an instruction the agent usually follows. With it, Claude Code blocks the edit. The hook uses Claude Code's `PreToolUse` hook API, so other agents ignore it; there the approval gate relies on the instructions alone. Add this to `~/.claude/settings.json` (or `<project>/.claude/settings.json`), merging into any existing `hooks` block:

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

The hook does nothing unless `<project>/.ui-tweak/pending` exists, so it costs nothing on other work. It doesn't see shell commands (`sed -i`, `cat >`), so it's a guard rail, not a sandbox. To override it mid-review, delete `.ui-tweak/pending`.

### 3. Ignore the mocks in git

Mocks are written to `<project>/.ui-tweak/`. The agent adds it to `.gitignore` if needed; to do it yourself:

```bash
echo ".ui-tweak/" >> .gitignore
```

## Use

In any project, just ask for a visual change:

- "make the pricing CTA more prominent"
- "redesign the signup form, two columns on desktop"
- "/ui-tweak the settings page feels cramped"

The agent will:

1. **Understand**: find the screen, your design tokens, and the app's component for every element on it.
2. **v1**: build `.ui-tweak/<slug>/v1.html`, start the server and open `http://localhost:4517/<slug>/latest`.
3. **Iterate**: each piece of feedback becomes `v2.html`, `v3.html`… (copied from the previous version, then edited). Keep the `/latest` tab open; it reloads itself.
4. **Implement**: only after "implement", "ship it" or "apply it". It edits your real code with the smallest diff.
5. **Verify**: runs your checks and, if it can, screenshots the result to compare with the approved version.

Shortcuts:
- "skip the preview" / "just do it": goes straight to the code.
- "go back to v2's header": old versions are kept, so you can mix and match.
- `http://localhost:4517/` lists every mock and version.

### Run the scripts by hand

```bash
# <skill> is where ui-tweak is installed, e.g. ~/.claude/skills/ui-tweak for Claude Code
python3 <skill>/scripts/serve.py .ui-tweak                         # start the preview server
python3 <skill>/scripts/check_native.py .ui-tweak/<slug>/v2.html   # check a mock
kill "$(python3 -c 'import json;print(json.load(open(".ui-tweak/.server"))["pid"])')"  # stop the server
```

## The in-app rule

Every element in a mock (buttons, inputs, search boxes, dropdowns, date pickers, checkboxes, radios, toggles, sliders, tabs, tooltips, modals, everything) must look like **your app's own component**, never the browser default. `check_native.py` enforces this before each version is shown. If your app really has a styled native control (e.g. a checkbox built on `appearance: none`), mark it with `data-in-app="<why>"` and the checker skips it.

## Update / uninstall

```bash
npx skills update ui-tweak            # installed with npx
npx skills remove ui-tweak

rm -rf <skills-folder>/ui-tweak       # installed by hand (for a symlink this removes only the link)
```

and, in Claude Code, remove the hook entry from `settings.json` if you added it.
