# skills-bag

Agent skills I build and use with Claude Code. Each one lives in `skills/<name>/` and installs on its own.

| Skill | What it does |
|---|---|
| [ui-tweak](skills/ui-tweak) | Preview-first UI changes: builds a versioned HTML mock from your app's real styles and in-app components, serves it on a live-reload server, iterates with you, and only touches your code after you say **implement**. Works for small tweaks and full redesigns. |

## Install

With the [`skills`](https://github.com/vercel-labs/skills) CLI (needs Node.js):

```bash
# one skill, for Claude Code, in every project
npx skills add https://github.com/yashu183/skills-bag --skill ui-tweak -a claude-code -g
```

- `--skill <name>` picks one skill from this repo. Leave it out to choose from a list.
- `-a claude-code` installs for Claude Code only. Leave it out to pick agents (Cursor, Codex, …).
- `-g` makes it available in all your projects. Without it, the skill is installed in the current project only.

Then start a new Claude Code session and type `/skills` to check it's there.

### Without npx

```bash
git clone https://github.com/yashu183/skills-bag.git
mkdir -p ~/.claude/skills
cp -R skills-bag/skills/ui-tweak ~/.claude/skills/        # or: ln -s "$PWD/skills-bag/skills/ui-tweak" ~/.claude/skills/ui-tweak
```

A symlink keeps you on the latest version with `git pull`; a copy stays as it is.

### Extra setup per skill

Some skills have optional pieces the installers can't set up, such as a hook in `settings.json`. Each skill's README says what they are. For ui-tweak, see [its README](skills/ui-tweak/README.md#2-the-guard-hook-optional).

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
```
