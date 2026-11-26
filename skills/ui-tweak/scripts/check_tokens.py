#!/usr/bin/env python3
"""Flag values in a mock's Proposed design that aren't in the design system.

Usage:
  python3 check_tokens.py <mock.html> --tokens <source> [--tokens <source> ...]

A <source> is any file that holds the design system's tokens: CSS/SCSS with
custom properties, design-token JSON (W3C / Style Dictionary / Tokens Studio,
or any nested JSON), a Tailwind config or JS/TS theme file, or a tokens.json
the agent wrote from external docs or Figma. Pass a folder to read every
token-like file inside it.

What is checked (only the Proposed design, never the Current panel or the
preview chrome):
  - the "PROPOSED STYLES" block of the template's <style>
  - style="" attributes inside .pv-option blocks
  - Tailwind arbitrary values in class="" inside .pv-option blocks (p-[13px], bg-[#123456])

What is flagged:
  - colours (hex, rgb/rgba, hsl/hsla, oklch, ...) that no token has
  - padding / margin / gap / border-radius / font-size lengths that no token has
  - var(--name) where --name is neither a token nor defined in the mock

Opt out for a deliberate exception:
  HTML:  data-off-system="<why>"   on the element
  CSS:   /* off-system: <why> */   on the same line as the declaration
Exit code 1 if anything unacknowledged is found.
"""
import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser

COLOR = re.compile(
    r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\([^)]*\)", re.I)
LENGTH = re.compile(r"(?<![\w.#-])(-?\d*\.?\d+)(px|rem)\b", re.I)
VAR = re.compile(r"var\(\s*(--[\w-]+)")
CSS_VAR_DEF = re.compile(r"(--[\w-]+)\s*:\s*([^;}{]+)")
SIZED_PROPS = re.compile(
    r"^(padding|margin)(-(top|right|bottom|left|inline|block)(-(start|end))?)?$"
    r"|^(row-|column-)?gap$|^border(-[a-z]+)*-radius$|^font-size$", re.I)
TW_SIZED = re.compile(
    r"^-?(p[xytrblse]?|m[xytrblse]?|gap(-[xy])?|space-[xy]|rounded(-[a-z]{1,2})?|text)$")
TOKEN_EXT = {".css", ".scss", ".sass", ".less", ".json", ".js", ".mjs", ".cjs",
             ".ts", ".mts", ".cts", ".md", ".txt", ".yaml", ".yml"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "source", "track", "wbr"}


def norm_color(c):
    c = c.strip().lower()
    if c.startswith("#"):
        h = c[1:]
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h)
        if len(h) == 8 and h.endswith("ff"):
            h = h[:6]
        return "#" + h
    m = re.match(r"rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)\s*(?:[,/]\s*([\d.]+%?))?\s*\)", c)
    if m:
        r, g, b = (round(float(x)) for x in m.group(1, 2, 3))
        a = m.group(4)
        hx = "#%02x%02x%02x" % (r, g, b)
        if a is None or a in ("1", "1.0", "100%"):
            return hx
        alpha = float(a[:-1]) / 100 if a.endswith("%") else float(a)
        return hx + "%02x" % round(alpha * 255)
    return re.sub(r"\s+", " ", re.sub(r"\s*([(),/])\s*", r"\1", c))


def norm_len(num, unit):
    px = float(num) * (16 if unit.lower() == "rem" else 1)
    return round(px, 3)


class Tokens:
    def __init__(self):
        self.colors, self.lengths, self.names = set(), set(), set()

    def add_text(self, text):
        for c in COLOR.findall(text):
            self.colors.add(norm_color(c))
        for num, unit in LENGTH.findall(text):
            self.lengths.add(norm_len(num, unit))
        for name, _ in CSS_VAR_DEF.findall(text):
            self.names.add(name)

    def add_json(self, data, path=()):
        if isinstance(data, dict):
            if "$value" in data or ("value" in data and not isinstance(data["value"], (dict, list))):
                self.add_json(data.get("$value", data.get("value")), path)
                return
            for k, v in data.items():
                if not str(k).startswith("$"):
                    self.add_json(v, path + (str(k),))
        elif isinstance(data, list):
            for v in data:
                self.add_json(v, path)
        else:
            if path:
                parts = [p for p in path if p not in ("DEFAULT", "default")]
                for i in range(len(parts)):
                    self.names.add("--" + "-".join(parts[i:]))
            if isinstance(data, (int, float)) and not isinstance(data, bool):
                self.lengths.add(round(float(data), 3))
            elif isinstance(data, str):
                self.add_text(data)
                if re.fullmatch(r"-?\d*\.?\d+", data.strip()):
                    self.lengths.add(round(float(data), 3))

    def load(self, path):
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in ("node_modules", ".git")]
                for f in files:
                    if os.path.splitext(f)[1].lower() in TOKEN_EXT:
                        self.load(os.path.join(root, f))
            return
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        if path.lower().endswith(".json"):
            try:
                self.add_json(json.loads(text))
                return
            except ValueError:
                pass
        self.add_text(text)


class ProposedHTML(HTMLParser):
    """Collect style/class attributes inside .pv-option blocks, with line numbers."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.depth_in, self.items, self.defined = [], None, [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        if self.depth_in is None and "pv-option" in cls.split():
            self.depth_in = len(self.stack)
        if self.depth_in is not None and "data-off-system" not in a:
            line = self.getpos()[0]
            if a.get("style"):
                self.items.append(("style", a["style"], line))
            if cls:
                self.items.append(("class", cls, line))
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack:
            top = self.stack.pop()
            if top == tag:
                break
        if self.depth_in is not None and len(self.stack) <= self.depth_in:
            self.depth_in = None


def proposed_css(text):
    """(css, first_line) of the PROPOSED STYLES block, or None."""
    m = re.search(r"PROPOSED STYLES[^\n]*\n", text)
    if not m:
        return None
    end = text.find("</style>", m.end())
    end = len(text) if end == -1 else end
    return text[m.end():end], text.count("\n", 0, m.end()) + 1


def check_decls(css, first_line, tokens, defined, where):
    problems = []
    # Drop comments (keeping line numbers), except the off-system markers.
    css = re.sub(r"/\*(?!\s*off-system).*?\*/", lambda m: "\n" * m.group(0).count("\n"), css, flags=re.S)
    for i, line in enumerate(css.split("\n")):
        if re.search(r"/\*\s*off-system", line):
            continue
        for decl in re.findall(r"([\w-]+)\s*:\s*([^;{}]+)", line):
            problems += check_value(decl[0], decl[1], tokens, defined, f"{where}:{first_line + i}")
    return problems


def check_value(prop, value, tokens, defined, loc):
    out = []
    for c in COLOR.findall(value):
        if norm_color(c) not in tokens.colors:
            out.append(f"{loc}: colour {c} ({prop}) is not a design-system token")
    if SIZED_PROPS.match(prop):
        for num, unit in LENGTH.findall(value):
            if float(num) != 0 and norm_len(num, unit) not in tokens.lengths:
                out.append(f"{loc}: {num}{unit} ({prop}) is not on the design system's scale")
    for name in VAR.findall(value):
        if name not in tokens.names and name not in defined:
            out.append(f"{loc}: var({name}) is not a design-system token")
    return out


def check_classes(cls, tokens, defined, loc):
    out = []
    for c in cls.split():
        m = re.match(r"^(?:[\w-]+:)*(-?[a-z-]+?)-\[(.+)\]$", c)
        if not m:
            continue
        prefix, val = m.group(1), m.group(2).replace("_", " ")
        for col in COLOR.findall(val):
            if norm_color(col) not in tokens.colors:
                out.append(f"{loc}: class {c}: colour {col} is not a design-system token")
        if TW_SIZED.match(prefix):
            for num, unit in LENGTH.findall(val):
                if float(num) != 0 and norm_len(num, unit) not in tokens.lengths:
                    out.append(f"{loc}: class {c}: {num}{unit} is not on the design system's scale")
        for name in VAR.findall(val):
            if name not in tokens.names and name not in defined:
                out.append(f"{loc}: class {c}: var({name}) is not a design-system token")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mocks", nargs="+")
    ap.add_argument("--tokens", action="append", required=True, help="token source file or folder (repeatable)")
    args = ap.parse_args()

    tokens = Tokens()
    for src in args.tokens:
        if not os.path.exists(src):
            sys.exit(f"token source not found: {src}")
        tokens.load(src)
    if not (tokens.colors or tokens.lengths or tokens.names):
        sys.exit("no tokens found in the given sources; point --tokens at the design system's token files")

    problems = []
    for path in args.mocks:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        text_nc = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
        defined = {n for n, _ in CSS_VAR_DEF.findall(text_nc) if not n.startswith("--pv-")}
        block = proposed_css(text_nc)
        if block:
            problems += check_decls(block[0], block[1], tokens, defined, path)
        parser = ProposedHTML()
        parser.feed(text_nc)
        for kind, val, line in parser.items:
            loc = f"{path}:{line}"
            if kind == "style":
                for prop, v in re.findall(r"([\w-]+)\s*:\s*([^;]+)", val):
                    problems += check_value(prop, v, tokens, defined, loc)
            else:
                problems += check_classes(val, tokens, defined, loc)

    for p in problems:
        print(p)
    if problems:
        print(f"\n{len(problems)} off-system value(s). Use the design system's token instead, or mark a "
              "deliberate exception (data-off-system=\"<why>\" / /* off-system: <why> */) and flag it "
              "to the user in the notes.")
        return 1
    print(f"OK: the proposed design uses only design-system values "
          f"({len(tokens.colors)} colours, {len(tokens.lengths)} sizes, {len(tokens.names)} token names loaded).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
