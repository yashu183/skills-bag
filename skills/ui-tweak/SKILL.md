---
name: ui-tweak
description: Preview-first workflow for any visual change to an existing app's UI, from a small tweak to a full redesign of a screen or flow. Builds a versioned HTML mock (v1, v2, …) from the app's real styles and in-app components, serves it on a live-reload local server, iterates with the user, and only edits application source after explicit approval ("implement", "ship it", "apply it"). Use this whenever the user asks to tweak, restyle, redesign, revamp, modernise, re-layout, move, resize, recolor or "make it look better" for any part of an existing interface (button, header, card, form, table, modal, nav, settings page, dashboard, onboarding, dark mode, spacing, typography), even if they don't ask for a preview, and when they type /ui-tweak. Not for backend work, brand-new apps from scratch, or pure UI bug fixes with no visual decision to make.
---

# UI tweak / redesign: mock → review → implement

The user wants to *see* a UI change and agree on it before any real code changes. Editing source first means they review a diff they can't picture, then revert it when it's wrong. A cheap HTML mock turns that into a quick visual conversation. Until the user approves, the mock is the work product, and app source stays untouched.

This covers everything from a one-button tweak to redesigning a whole screen. For a redesign, the mock is a full screen (or a few key screens/states), and offering 2–3 distinct directions as options is usually worth it.

Fast path: if the user says "skip the preview", "just do it", or similar, go straight to Phase 4. Their call beats the workflow.

## The one rule that keeps getting broken: in-app components only

**Every UI element** in a mock must look like **the app's own component**, never the browser's default. This means every element, not a fixed list. Common ones: buttons, links, text inputs, textareas, search boxes, number fields, dropdowns/selects, comboboxes, date and time pickers/calendars, checkboxes, radio buttons, toggle switches, sliders, file uploads, tabs, menus, tooltips, popovers, modals/dialogs, toasts, badges, tables, pagination, progress bars, spinners, avatars, and scrollbars where the app styles them. If an element isn't on that list, the rule still applies.

A browser-default element (a native `<select>`, `<input type="date">`, an unstyled `<input>` or `<button>`, a plain checkbox) renders as the browser's widget. It doesn't look like the app, so the user can't judge the design, and it tends to get copied into the real code. This mistake has happened repeatedly, so treat it as a hard requirement:

- In Phase 1, list **every** element the change shows and find the app's component or styling for each one (see `references/mock-fidelity.md`, "Component inventory"). That includes the plain ones like text inputs, search fields and buttons, not just the fancy ones.
- Rebuild each control in the mock from that component's real markup and classes, including its open state when that matters (an open dropdown list, an open calendar).
- Even when an element is built on a native tag (most apps' text inputs are `<input>` with classes), it must carry the app's exact classes/styles: border, radius, height, padding, focus ring, placeholder colour, icon placement (e.g. the search icon inside the field).
- If the app has no component for a control, don't fall back to native. Say so in the mock's notes, design one in the app's visual language, and ask whether to add it to the app's component library.
- Before showing **every** version, run `python3 <skill-dir>/scripts/check_native.py <the version file>`. Fix everything it flags. The only exception is an element that really matches the app, e.g. the app's own styled checkbox built on `appearance: none`; mark that one with `data-in-app="<why>"`.
- The same applies in Phase 4: use the app's components in the real code, never native ones.

## Where the mocks live

```
<project>/.ui-tweak/
  pending                 ← slug of the mock under review (the approval gate)
  .server                 ← the running preview server's URL (written by serve.py)
  <short-slug>/
    v1.html
    v2.html               ← each round of feedback = a new version
    …
```

If the repo uses git and `.ui-tweak/` isn't ignored, add it to `.gitignore`.

## Phase 1 — Understand (read-only)

1. Find the component(s) or screen(s) the request touches.
2. Find where the visual language lives: design tokens, CSS variables, Tailwind config, theme files, fonts, icon set. `references/mock-fidelity.md` says where to look per stack. Read it the first time you work in a repo.
3. Take the component inventory (above): every element the change shows → the app's component or styling that provides it.
4. Restate the request in one line ("Redesign the trial signup form: two columns on desktop, plan picker as cards instead of a dropdown"). Ask a question only if two readings would give visibly different designs. Otherwise pick one and show the other as an option.

## Phase 2 — First mock (v1)

1. `mkdir -p .ui-tweak/<slug>` and copy the template: `cp <skill-dir>/assets/preview-template.html .ui-tweak/<slug>/v1.html`. Then fill in its placeholders with Edit.
2. Write the slug into `.ui-tweak/pending`. That marks a review in progress, and the optional guard hook checks it (`references/gate-guard.md`).
3. **Current** panel: rebuild the existing UI faithfully, with real colours, fonts, spacing, radii, copy and in-app controls. Use the actual token values, not lookalikes. A mock that doesn't look like their app makes the user judge the mock instead of the change.
4. **Proposed** panel: the change, built the same way. When there's a real design choice (always for a redesign), show 2–3 labelled options in the template's option tabs. Don't add options just to fill the tabs.
5. Fill in the notes: what changed, which tokens, classes and components it uses, and what the mock can't show.
6. Run `check_native.py` on v1.html and fix what it finds.
7. Start the preview server, or reuse it if it's already running. Run it in the background:
   `python3 <skill-dir>/scripts/serve.py <project>/.ui-tweak`
   It prints the URL, and if a server is already running for this folder it prints that URL and exits. Give the user `http://localhost:<port>/<slug>/latest`: that tab always shows the newest version and reloads itself when a new one appears. Open it for them (`open` on macOS, `xdg-open` on Linux). If you can't run a server, open the file directly instead.
8. Ask one direct question: "Which option, and what should change? Say **implement** when it's right."

## Phase 3 — Iterate: every round is a new version

When the user gives feedback, make the next version by **copying, then editing**:

```bash
cp .ui-tweak/<slug>/v2.html .ui-tweak/<slug>/v3.html
```

Then apply only the requested changes to `v3.html` with Edit. Don't rewrite a version from scratch with Write: most of the file is unchanged, regenerating it wastes tokens, and it risks drifting details the user already approved. Old versions stay untouched, so the user can compare and go back ("go back to v2's header").

For each new version:
- Add a changelog line in the notes ("v3: badge moved into the header; CTA radius 8 → 12").
- Drop options the user rejected, so the mock narrows toward a decision.
- Run `check_native.py` on it.
- Tell the user it's up: their `/latest` tab reloads on its own. Mention the version number.

Stay in this phase until the user approves. "Looks good" or "nice" on its own is ambiguous, so confirm with "Want me to implement v3 now?" rather than guessing. Clear approvals: "implement", "ship it", "apply it", "go ahead and build it", "do option B of v2".

## Phase 4 — Implement (only after approval)

1. Delete `.ui-tweak/pending` first, so the guard (if installed) stops blocking edits.
2. Apply the **approved version** (name it: "implementing v3, option B") with the smallest diff that achieves it.
   - Use the app's components from the inventory, and reuse existing tokens, variables and utility classes. Don't hard-code a value that already has a token.
   - Match the file's existing conventions (class ordering, styling approach, naming).
   - Touch only what the approved mock changed. Unrelated cleanup is a separate conversation.
3. If the design needs a value with no token, or a component the app doesn't have, say so and ask how to handle it.

## Phase 5 — Verify

1. Run the project's type check / lint / tests if they're quick and normally used.
2. If you can run the app and take a screenshot (a browser tool, Playwright, or the project's run skill), capture the changed screen and compare it with the approved version. Check the controls are the app's components, then report any visible difference plainly ("spacing under the title is 16px in the app vs 24px in v3 — the parent container adds padding").
3. If you can't run it, say so and tell the user exactly which page and state to check.
4. Leave `.ui-tweak/<slug>/` in place as the design record. Stop the preview server if the user is done with it (its PID is in `.ui-tweak/.server`).

## Mock-building tips

- Static HTML + inline CSS is enough. Load the app's real font (Google Fonts or the local font files); if you can't, name the fallback in the notes.
- For Tailwind projects, the template can load the Tailwind CDN with the project's theme pasted in. The mock then uses the same class names as the real code, which makes Phase 4 nearly a copy-paste (`references/mock-fidelity.md`).
- Show the states that matter for this change: hover/focus, open dropdown or calendar, empty/error/long text, mobile width. The template's viewport buttons (360 / 768 / 1280) resize both panels.
- Use realistic content from the app (real labels, plausible data), not lorem ipsum.
