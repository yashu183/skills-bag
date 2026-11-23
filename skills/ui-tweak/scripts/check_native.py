#!/usr/bin/env python3
"""Flag browser-default elements in a mock (or any HTML/JSX file).

Usage:  python3 check_native.py <file> [<file> ...]

Mocks must show the app's own components: a native <select> or date input
renders as the browser's widget, not the app's, and gets copied into the
real code. This lists every native control so each one is either replaced
with the app's component or explicitly acknowledged.

Acknowledge a deliberate one by adding  data-in-app="<why>"  to the element,
e.g. when the app itself really uses a styled native checkbox
(appearance:none + its own CSS). Exit code 1 if anything is unacknowledged.
"""
import re, sys

CHECKS = [
    (r"<select\b", "native <select> dropdown: use the app's Select/Dropdown/Combobox"),
    (r"<datalist\b", "native <datalist>: use the app's Combobox/Autocomplete"),
    (r"<input\b[^>]*\btype\s*=\s*['\"]?(date|time|datetime-local|month|week)\b", "native date/time picker: use the app's DatePicker/Calendar"),
    (r"<input\b[^>]*\btype\s*=\s*['\"]?(checkbox|radio)\b", "native checkbox/radio: use the app's Checkbox/Radio/Switch"),
    (r"<input\b[^>]*\btype\s*=\s*['\"]?range\b", "native range: use the app's Slider"),
    (r"<input\b[^>]*\btype\s*=\s*['\"]?color\b", "native color picker: use the app's ColorPicker"),
    (r"<input\b[^>]*\btype\s*=\s*['\"]?file\b", "native file input: use the app's upload/dropzone component"),
    (r"<input\b[^>]*\btype\s*=\s*['\"]?search\b", "native search input (browser clear button): use the app's SearchInput, or hide ::-webkit-search-cancel-button and style it like the app"),
    (r"<input\b[^>]*\btype\s*=\s*['\"]?number\b", "native number input (browser spinners): use the app's NumberInput, or hide the spin buttons and style it like the app"),
    (r"<(progress|meter)\b", "native <progress>/<meter>: use the app's Progress"),
    (r"<dialog\b", "<dialog>: use the app's Modal/Dialog styling"),
    (r"\btitle\s*=\s*['\"][^'\"]+['\"]", "title= tooltip: use the app's Tooltip"),
    (r"\b(alert|confirm|prompt)\s*\(", "alert/confirm/prompt: use the app's Toast/Dialog"),
]


def main(paths):
    problems = 0
    for path in paths:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        # Ignore the preview chrome's own <title> and the HTML comments.
        scan = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
        scan = re.sub(r"<title>.*?</title>", "", scan, flags=re.S | re.I)
        for pattern, why in CHECKS:
            for m in re.finditer(pattern, scan, flags=re.I):
                tag_end = scan.find(">", m.start())
                tag = scan[m.start(): tag_end + 1 if tag_end != -1 else m.end()]
                if "data-in-app" in tag:
                    continue
                line = scan.count("\n", 0, m.start()) + 1
                print(f"{path}:{line}: {why}\n    {tag[:120].strip()}")
                problems += 1
        # Form elements with no styling at all render as browser defaults.
        for m in re.finditer(r"<(input|textarea|button)\b[^>]*>", scan, flags=re.I):
            tag = m.group(0)
            if "data-in-app" in tag or re.search(r"\btype\s*=\s*['\"]?hidden\b", tag, re.I):
                continue
            if not re.search(r"\b(class|className|style)\s*=", tag):
                line = scan.count("\n", 0, m.start()) + 1
                print(f"{path}:{line}: unstyled <{m.group(1).lower()}> renders as the browser default: "
                      f"give it the app's classes/styles (or data-in-app if a parent selector styles it)\n    {tag[:120].strip()}")
                problems += 1
    if problems:
        print(f"\n{problems} native control(s) found. Replace each with the app's component, "
              "or add data-in-app=\"<reason>\" if it truly matches the app.")
        return 1
    print("OK: no unacknowledged native controls.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
