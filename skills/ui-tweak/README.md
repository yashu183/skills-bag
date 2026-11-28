# ui-tweak

An agent skill for UI changes: **preview first, code later**.

It uses the open [Agent Skills](https://agentskills.io) format (`SKILL.md` + plain Python scripts), so it works in any coding agent that supports skills: Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI and others. The one exception is the optional [guard hook](#optional-the-guard-hook-claude-code-only), which is Claude Code-only.

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
│   ├── design-system.md      finding the app's design system (repo, npm package, docs/Figma you name), the digest, in-system options
│   └── gate-guard.md         the optional hook (Claude Code only): what it does, the escape hatch
├── scripts/
│   ├── serve.py              live-reload preview server for .ui-tweak/ (port 4517+)
│   ├── check_native.py       fails if a mock uses browser-default controls instead of in-app ones
│   ├── check_tokens.py       fails if the proposed design uses colours/sizes that aren't design-system tokens
│   └── ui-tweak-guard.sh     optional Claude Code PreToolUse hook: blocks source edits while a mock is under review
├── assets/
│   └── preview-template.html the frame every mock starts from (Current / Proposed panels, viewports, dark mode, notes)
└── evals/                    5 execution test cases + trigger-evals.json (should / shouldn't trigger queries)
```

## Requirements

- A coding agent that supports Agent Skills (Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, …)
- `python3` on your PATH (the scripts use only the standard library; nothing to `pip install`)

## Install

See the [repo README](../../README.md#install) for installing with the `skills` CLI or by hand.

### Optional: the guard hook (Claude Code only)

A Claude Code hook that blocks source edits while a mock is under review. Setup: [docs/ui-tweak-guard.md](../../docs/ui-tweak-guard.md).

### Ignore the mocks in git

Mocks are written to `<project>/.ui-tweak/`. The agent puts a `.gitignore` containing `*` inside that folder, so git ignores it without any change to your repo's own `.gitignore`. Nothing to do on your side.

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
python3 <skill>/scripts/check_native.py .ui-tweak/<slug>/v2.html   # check a mock for browser-default controls
python3 <skill>/scripts/check_tokens.py .ui-tweak/<slug>/v2.html --tokens <token file or folder>   # check it against the design system
kill "$(python3 -c 'import json;print(json.load(open(".ui-tweak/.server"))["pid"])')"  # stop the server
```

## The in-app rule

Every element in a mock (buttons, inputs, search boxes, dropdowns, date pickers, checkboxes, radios, toggles, sliders, tabs, tooltips, modals, everything) must look like **your app's own component**, never the browser default. `check_native.py` enforces this before each version is shown. If your app really has a styled native control (e.g. a checkbox built on `appearance: none`), mark it with `data-in-app="<why>"` and the checker skips it.

## Design systems

If your app has a design system, ui-tweak treats it as the source of truth. It finds it wherever it lives:

- **in the repo:** a design doc such as `DESIGN.md` or `design.md` (any letter case, any folder), a `design-system/` or `packages/ui` folder, token JSON, Storybook
- **in a published package:** e.g. `@acme/ui` in `node_modules`, with its token CSS/JSON and component types
- **in external docs or Figma, only if you name it:** by default the agent never goes outside your repo, so a private design system stays private. For a public docs site it reads the pages. For a private one (SSO, internal wiki, private Figma) it uses a connector your agent already has; otherwise it asks you to export the tokens to `.ui-tweak/tokens.json` or paste the rules. It never asks for credentials.

To skip the search, tell it where to look ("our design system is `@acme/ui`, docs at design.acme.dev").

It saves what it found (sources, token files, components, rules) to `.ui-tweak/design-system.md` in your project, so later mocks reuse it.

**Options stay inside the system.** The 2–3 options differ in layout, hierarchy, density and which existing components they use, never in invented colours, sizes or components. If your request needs something the system doesn't have, the agent says so and asks before using it. `check_tokens.py` enforces this before each version is shown. It flags colours and padding, margin, gap, radius and font-size values in the proposed design that aren't tokens. A deliberate exception is marked `data-off-system="<why>"` (HTML) or `/* off-system: <why> */` (CSS) and listed in the mock's notes.

## Security scan

Checked with [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector) (static mode, `--no-llm`): no findings.

`SKILL.md` declares its tool scope in `allowed-tools`, and each grant is scoped:

| Grant | Why |
|---|---|
| `Read Grep Glob` | read the app's styles and components |
| `Write(.ui-tweak/**) Edit(.ui-tweak/**)` | write and edit the mocks, **only** inside `.ui-tweak/` |
| `WebFetch(domain:localhost)` | load the local preview server |

In the Agent Skills format, `allowed-tools` pre-approves tools in the agents that honour it. Because writes and edits are limited to `.ui-tweak/`, edits to your app's source still go through your agent's normal permission prompt, so the approval step stays intact. Tool names and the `Tool(scope)` syntax vary by agent; an agent that doesn't recognise a grant ignores it and asks for permission as usual.

## Update / uninstall

See the [repo README](../../README.md#update--uninstall). If you added the guard hook, also remove its entry from `settings.json`.
