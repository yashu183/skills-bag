# skills-bag

Agent skills I build and use. Each one lives in `skills/<name>/` and installs on its own.

They use the open [Agent Skills](https://agentskills.io) format (a `SKILL.md` plus plain scripts), so they work in any coding agent that supports skills: Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI and others. Anything agent-specific, like a Claude Code hook, is optional and called out in that skill's README.

| Skill | What it does |
|---|---|
| [ui-tweak](skills/ui-tweak) | Preview-first UI changes: builds a versioned HTML mock from your app's real styles and in-app components, serves it on a live-reload server, iterates with you, and only touches your code after you say **implement**. Works for small tweaks and full redesigns. |

## Install

With the [`skills`](https://github.com/vercel-labs/skills) CLI (needs Node.js):

```bash
# one skill, in every project; asks which agents to install for
npx skills@1.9.0 add https://github.com/yashu183/skills-bag --skill ui-tweak -g
```

The `skills` CLI is pinned to a version you can check, rather than whatever is latest on npm. Bump it when you want a newer one.

- `--skill <name>` picks one skill from this repo. Leave it out to choose from a list.
- `-a <agent>` skips the agent picker, e.g. `-a claude-code`. Leave it out to pick agents (Claude Code, Cursor, Codex, …).
- `-g` makes it available in all your projects. Without it, the skill is installed in the current project only.

Then start a new session in your agent. In Claude Code, type `/skills` to check it's there.

### Without npx

Copy or symlink the skill folder into your agent's skills folder (check its docs for the path). For Claude Code:

```bash
git clone https://github.com/yashu183/skills-bag.git
mkdir -p ~/.claude/skills
cp -R skills-bag/skills/ui-tweak ~/.claude/skills/        # or: ln -s "$PWD/skills-bag/skills/ui-tweak" ~/.claude/skills/ui-tweak
```

A symlink keeps you on the latest version with `git pull`; a copy stays as it is.

### Extra setup per skill

Some skills have optional pieces the installers can't set up, such as a Claude Code hook in `settings.json`. They're documented in `docs/`. For ui-tweak: [the guard hook](docs/ui-tweak-guard.md) (Claude Code only).

## Update / uninstall

```bash
npx skills@1.9.0 update ui-tweak     # installed with npx
npx skills@1.9.0 remove ui-tweak

rm -rf ~/.claude/skills/ui-tweak     # installed by hand into Claude Code (for a symlink this removes only the link)
```

## Layout

```
skills/
  <name>/
    SKILL.md        instructions the agent loads when the skill triggers
    README.md       for humans: what it does, how to install and use it
    references/     docs the agent reads only when needed
    scripts/        code the agent runs
    assets/         files the agent copies into its output
    evals/          test cases for the skill (skill-creator / `claude plugin eval` format)
docs/               setup guides for optional, agent-specific extras (e.g. hooks)
```

Everything inside `skills/<name>/` gets installed. Agent-config setup (hooks, `settings.json`) lives in `docs/` instead, so the skill itself never tells an agent to touch its own config.
