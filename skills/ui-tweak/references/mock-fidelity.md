# Making the mock look like the real app

The mock is only useful if the user recognises their own app in it. Read the app's styling sources first and copy the real values.

## Where the visual language lives, by stack

| Stack signal | Read these |
| --- | --- |
| `tailwind.config.*` or `@import "tailwindcss"` / `@theme` in CSS | The config's `theme.extend` (v3) or `@theme { … }` blocks (v4), plus the global CSS that defines CSS variables. The component's class list is the spec. |
| CSS variables (`:root { --… }`) | Global stylesheet(s): `globals.css`, `index.css`, `app.css`, `styles/*.css`, including `.dark` / `[data-theme]` overrides. |
| shadcn/ui | `components.json`, `globals.css` (HSL/OKLCH variables), `components/ui/*` for the base component's classes. |
| MUI | `createTheme(...)` call (palette, typography, shape.borderRadius, spacing), plus `sx` / `styled` overrides on the component. |
| Chakra / Mantine | The theme file passed to the provider (`extendTheme`, `createTheme`). |
| styled-components / Emotion | The `ThemeProvider` theme object plus the component's styled block. |
| CSS / SCSS modules | The component's `.module.css` / `.scss`, and SCSS variables/mixins it imports. |
| Vue / Svelte / Angular | The component's `<style>` block (scoped) plus global styles. |
| React Native / Flutter | StyleSheet / ThemeData. Mock at a phone width (360–430). |

Also check:
- **Fonts:** `next/font` calls, `@font-face`, `<link>` tags in the root layout or `index.html`.
- **Icons:** which set (lucide, heroicons, material). Use the same set's SVGs from a CDN, or copy the inline SVG.
- **Dark mode:** if the app has one and the change touches colour, show both themes (the template has a theme toggle).

## Component inventory (in-app controls)

Before building, list **every** element the mock shows (buttons, inputs, search fields, textareas, selects, date pickers, checkboxes, radios, toggles, sliders, uploads, tabs, menus, tooltips, modals, toasts, badges, tables, pagination, and anything else) and find the app's own component or styling for each. Rebuild the mock from that component's markup and classes, never from the browser's native element. Plain-looking elements count too: a text input or search box built with the app's classes looks very different from a bare `<input>`.

| Stack | Where the app's components live |
| --- | --- |
| shadcn/ui | `components/ui/*.tsx` (select, popover + calendar, checkbox, switch, tooltip, dialog, sonner/toast). Radix underneath: copy the trigger *and* the open content's classes. |
| Radix / Headless UI / Ark | The app's wrapper components, usually under `components/` or `ui/`. |
| MUI | `Select`/`Autocomplete`, `DatePicker` (`@mui/x-date-pickers`), `Checkbox`, `Switch`, `Tooltip`, `Dialog`, plus the theme's `components` overrides. |
| Chakra / Mantine / Ant Design | The library's components plus theme overrides. Mirror their DOM and class names, and take the colours from the theme. |
| Custom design system | See `design-system.md` for the full search (repo, published package, docs/Figma). Components usually live in `components/`, `ui/`, `design-system/` or a workspace package such as `packages/ui`. Search for `Select`, `Dropdown`, `DatePicker`, `Calendar`, `Checkbox`, `Toggle`, `Tooltip`, `Modal`, `Toast`. |
| Plain HTML/CSS sites | The site's CSS for `.select`, `.dropdown`, `.datepicker` etc. If the site truly uses native controls with custom CSS (`appearance: none`), mirror that CSS and mark the element `data-in-app`. |

Quick search: `grep -rliE "button|input|textarea|search|select|dropdown|combobox|datepicker|calendar|checkbox|radio|switch|toggle|slider|upload|tabs|menu|tooltip|popover|dialog|modal|toast|badge|table|pagination" src components app packages 2>/dev/null`

If a control has no in-app component, don't fall back to native. Design one in the app's language, flag it in the notes, and ask whether to add it to the app.

When the open state matters (a dropdown's list, a calendar's month grid), show it in the mock as a static open panel next to or under the closed control. The user needs to see what the app's popover looks like, not just the trigger.

## Rebuilding the current UI

- Copy the real markup structure and copy text. Replace framework components with plain HTML that has the same computed styles.
- Copy token values exactly (hex/HSL/OKLCH, px/rem, radii, shadows).
- If the component depends on data, use one realistic record from fixtures, seed data or the UI's own labels.
- If the app is running and a browser tool is available, a screenshot of the real screen is a good reference for the "Current" panel's accuracy. You can also embed the screenshot as the Current panel and build only the Proposed side, when rebuilding is costly. Say so in the notes.

## Tailwind shortcut

When the project uses Tailwind, add the Play CDN to the mock and paste the project's theme extension in, so the mock uses the real class names:

```html
<script src="https://cdn.tailwindcss.com/3.4.16"></script>
<script>
  tailwind.config = { theme: { extend: { /* paste from tailwind.config */ } } }
</script>
```

For Tailwind v4 (`@theme` in CSS), use `@tailwindcss/browser` and paste the `@theme` block into a `<style type="text/tailwindcss">` tag:

```html
<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4.1.11"></script>
<style type="text/tailwindcss">
  @theme { /* paste the project's @theme block */ }
</style>
```

The proposed panel's classes can then be copied almost directly into the component in Phase 4.
