#!/usr/bin/env python3
"""Static sanity checks for the profile README.

Not a GitHub renderer: it catches broken asset paths, unbalanced HTML, missing
alt text and anchors, duplicated ids, table shape mistakes and suspicious
attributes before the page is committed.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

VOID = {"br", "img", "source", "hr", "input", "meta", "link"}
ALLOWED_ATTRS = {
    "a": {"href", "id", "name", "title", "alt"},
    "img": {"src", "alt", "width", "height", "title", "align"},
    "source": {"media", "srcset", "type"},
    "table": {"width", "align"},
    "td": {"width", "valign", "align", "colspan", "rowspan"},
    "th": {"width", "valign", "align", "colspan", "rowspan"},
    "details": {"open"},
    "h2": {"id", "align"},
    "p": {"align"},
    "div": {"align"},
}


class Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.ids = []
        self.names = []
        self.images = []
        self.links = []
        self.tables = []
        self._row = None
        self._table = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ALLOWED_ATTRS:
            for k in a:
                if k not in ALLOWED_ATTRS[tag]:
                    self.errors.append(f"unexpected <{tag} {k}=...>")
        if "style" in a or "onclick" in a:
            self.errors.append(f"inline script/style on <{tag}>")
        if tag == "img":
            src = a.get("src", "")
            self.images.append((src, a.get("alt", "")))
            if not src:
                self.errors.append("img without src")
            elif not src.startswith("http") and not (ROOT / src.lstrip("./")).exists():
                self.errors.append(f"missing image: {src}")
            if not a.get("alt"):
                self.errors.append(f"img without alt: {src}")
        if tag == "source":
            ss = a.get("srcset", "")
            if ss and not ss.startswith("http") and not (ROOT / ss.lstrip("./")).exists():
                self.errors.append(f"missing source image: {ss}")
        if tag == "a":
            if "id" in a:
                self.ids.append(a["id"])
            if "name" in a:
                self.names.append(a["name"])
            if "href" in a:
                self.links.append(a["href"])
        if tag == "table":
            self._table = []
            self.tables.append(self._table)
            self._row = None
        elif tag == "tr" and self._table is not None:
            self._row = 0
            self._table.append(self._row)
        elif tag in ("td", "th") and self._row is not None:
            self._row += 1
            self._table[-1] = self._row
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"closing </{tag}> with empty stack")
            return
        if self.stack[-1] != tag:
            self.errors.append(f"mismatched </{tag}>, open: {self.stack[-4:]}")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()


def markdown_table_widths(text):
    issues = []
    in_code = False
    prev = None
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.strip().startswith("|") and line.strip().endswith("|"):
            cells = line.count("|") - 1
            if prev is not None and prev[1] != cells and not re.match(r"^\|[\s:|-]+\|$", line.strip()):
                issues.append(f"table row {n} has {cells} cells, previous {prev[1]}")
            prev = (n, cells)
        else:
            prev = None
    return issues


def main():
    text = README.read_text()
    parser = Checker()
    parser.feed(text)

    errors = list(parser.errors)
    if parser.stack:
        errors.append(f"unclosed tags: {parser.stack}")
    for t in parser.tables:
        if t and len(set(t)) != 1:
            errors.append(f"HTML table with uneven rows: {t}")

    # local files and anchors referenced from within the page
    for href in parser.links:
        if href.startswith(("./", "../")):
            if not (ROOT / href).exists():
                errors.append(f"missing local link target: {href}")
        if href.startswith("#"):
            target = href[1:]
            if target not in set(parser.ids) | set(parser.names):
                errors.append(f"internal link without anchor: {href}")

    if len(parser.ids) != len(set(parser.ids)):
        errors.append("duplicate ids")
    if len(parser.names) != len(set(parser.names)):
        errors.append("duplicate names")

    # markdown tables
    errors += markdown_table_widths(text)

    # asset weight
    assets = sorted((ROOT / "assets" / "wii").rglob("*"))
    total = sum(p.stat().st_size for p in assets if p.is_file())

    print(f"images: {len(parser.images)} · links: {len(parser.links)} · anchors: {len(set(parser.ids) | set(parser.names))}")
    print(f"assets/wii: {len([p for p in assets if p.is_file()])} files, {total / 1024:.0f} KB")
    if errors:
        print("\n".join(f"  ✗ {e}" for e in errors))
        return 1
    print("  ✓ README structure, assets and anchors look consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
