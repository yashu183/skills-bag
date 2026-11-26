# Working with the app's design system

When the app has a design system, it is the source of truth for every mock: its tokens, its components and its usage rules. The options you show differ in **how** they use the system, never by stepping outside it.

## 1. Find it

Check in this order and stop adding sources once you have the tokens, the components and the rules. A design system is often spread over several of these (tokens in a package, rules in a docs site), so collect from each one that exists.

1. **What the user named.** A path, package name, docs URL or Figma file they point to wins over anything you find.
2. **A digest from an earlier run:** `.ui-tweak/design-system.md` (see step 3). Reuse it unless the package version changed, the token files changed, or the user says the system was updated.
3. **Inside the repo:**
   - docs: any Markdown file named `design*` or `*design-system*` in **any letter case and any folder**, e.g. `DESIGN.md`, `design.md`, `Design-System.md`, `docs/design/*.md`, `packages/ui/DESIGN.md`. Also UI sections in `CONTRIBUTING`. Search case-insensitively, e.g. `find . \( -iname '*design*.md' -o -ipath '*/*design*/*.md' \) -not -path '*/node_modules/*' -not -path './.ui-tweak/*'` (the second pattern catches docs inside a `design/` or `design-system/` folder). Skip `.ui-tweak/design-system.md`: that's this skill's own digest, not the app's docs.
   - folders and workspace packages: `design-system/`, `packages/ui`, `packages/tokens`, `packages/design-system`, `libs/ui`
   - token files: `tokens/*.json`, `*.tokens.json`, Style Dictionary config (`config.json` / `sd.config.*`), Tokens Studio exports
   - Storybook: `.storybook/` and `*.stories.*` (the stories show each component's variants and intended use)
4. **A published package.** Look at `package.json` dependencies and at imports in the screen's components (`from "@acme/ui"`). Then read `node_modules/<package>/`:
   - `package.json` (`exports`, `style`, `version`)
   - token CSS or JSON in `dist/` (`tokens.css`, `variables.css`, `tokens.json`)
   - type definitions (`*.d.ts`) for each component's props: variants, sizes, tones
   - `README` or bundled docs
5. **External docs or Figma.**
   - Docs site: fetch the pages for the components and foundations (colour, spacing, type) the change touches.
   - Figma: if a Figma tool or connector is available, read the file's variables and components with it. Otherwise ask the user to export the variables (Figma variables or Tokens Studio JSON) and save the export as `.ui-tweak/tokens.json`.
   - Don't infer tokens from screenshots. If that's all there is, say so and treat the values as approximate.

If sources disagree, trust what ships in code (the package and token files the app actually imports) over docs, and docs over Figma. Tell the user about the disagreement.

If there's no design system, use the app's own styling as described in `mock-fidelity.md`. If the app defines CSS variables, those are its tokens, and `check_tokens.py` can still check against them.

## 2. Extract what the mock needs

- **Tokens:** colour (including dark-theme values), spacing scale, radii, type scale (size, weight, line height), shadows, breakpoints.
- **Components:** for each element in the component inventory, the design-system component, its variants and sizes, and its real markup and classes, which you copy into the mock.
- **Rules:** the usage guidance the docs give, e.g. "one primary button per view", "use Card for grouped content", "16px minimum body text", "danger colour only for destructive actions". These constrain the options as much as the tokens do.

## 3. Write the digest

Save what you found to `.ui-tweak/design-system.md` so later mocks in this project reuse it rather than searching again. Keep it short:

```markdown
# Design system digest (<date>)
Sources: packages/ui (workspace), @acme/tokens@4.2.0, https://design.acme.dev (docs)
Token files for check_tokens: node_modules/@acme/tokens/dist/tokens.css, packages/ui/src/theme.ts
Components: Button (primary|secondary|ghost; sm|md|lg), Card, Select, DatePicker, Badge (neutral|success|danger) ...
Rules: one primary action per view; spacing from --space-* only; body text >= 14px; ...
Gaps: no Stepper component; no token for 20px radius
```

## 4. Design options: strictly in-system

When a design system exists, every option in the Proposed panel uses **only** its tokens and components and follows its rules. Options may differ in:

- layout and arrangement (columns, order, alignment, grouping)
- hierarchy and emphasis (which existing variant is primary, what's visually loudest)
- density (which steps of the spacing scale and which component sizes)
- which existing components or variants carry the content (cards vs a list, tabs vs sections)

They must not invent colours, sizes, radii, shadows, fonts or components. If the request can't be met inside the system, say so, show the closest in-system option, and propose the addition separately ("needs a new `--radius-xl` token; approve?"). Don't build an option on it until the user agrees.

In the mock's "Design system" notes, list for each option the components and tokens it uses, and anything off-system with the reason.

## 5. Check every version

Put CSS that only the proposed design needs in the template's PROPOSED STYLES block. Then, before showing each version, run:

```bash
python3 <skill-dir>/scripts/check_tokens.py .ui-tweak/<slug>/vN.html --tokens <token file or folder> [--tokens ...]
```

Pass the token files listed in the digest. It checks only the Proposed design (the PROPOSED STYLES block, plus `style` and Tailwind arbitrary-value classes inside the options), not the Current panel, which may contain older values. It flags colours and padding, margin, gap, radius and font-size values that no token has, plus `var(--x)` references to tokens that don't exist. Fix what it flags with the right token. For an exception the user already approved, mark it with `data-off-system="<why>"` on the element or `/* off-system: <why> */` on the CSS line, and keep it listed in the notes.
