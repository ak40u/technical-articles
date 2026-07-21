#!/usr/bin/env python3
"""Verify that generated article diagrams remain readable and zoomable."""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path


EXPECTED_DIAGRAMS = 3


class DiagramParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.current: dict[str, object] | None = None
        self.diagrams: list[dict[str, object]] = []
        self.link_open = False

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs_list)
        classes = set((attrs.get("class") or "").split())

        if tag == "figure" and "diagram" in classes:
            self.current = {"link": None, "image": None, "action": False}
            self.link_open = False
            return

        if self.current is None:
            return

        if tag == "a" and "diagram-link" in classes:
            self.current["link"] = attrs
            self.link_open = True
        elif tag == "img" and self.link_open:
            self.current["image"] = attrs
        elif tag == "span" and "diagram-action" in classes and self.link_open:
            self.current["action"] = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self.link_open = False
        if tag == "figure" and self.current is not None:
            self.diagrams.append(self.current)
            self.current = None
            self.link_open = False


def read_html(source: str) -> str:
    if source == "-":
        return sys.stdin.read()
    return Path(source).read_text(encoding="utf-8")


def validate(source: str, css_source: str) -> list[str]:
    parser = DiagramParser()
    parser.feed(read_html(source))
    errors: list[str] = []

    if len(parser.diagrams) != EXPECTED_DIAGRAMS:
        errors.append(f"expected {EXPECTED_DIAGRAMS} zoomable diagrams, found {len(parser.diagrams)}")

    css = Path(css_source).read_text(encoding="utf-8")
    required_css = {
        "desktop breakout": "width: min(1200px, calc(100vw - 40px));",
        "mobile viewport fit": "width: calc(100vw - 24px);",
        "zoom affordance": "cursor: zoom-in;",
        "keyboard focus": ".diagram-link:focus-visible",
    }
    for label, fragment in required_css.items():
        if fragment not in css:
            errors.append(f"CSS: missing {label}")

    for index, diagram in enumerate(parser.diagrams, start=1):
        link = diagram["link"]
        image = diagram["image"]
        prefix = f"diagram {index}"

        if not isinstance(link, dict):
            errors.append(f"{prefix}: missing diagram link")
            continue
        if not isinstance(image, dict):
            errors.append(f"{prefix}: missing image")
            continue

        href = link.get("href") or ""
        src = image.get("src") or ""
        rel = set((link.get("rel") or "").split())

        if not href.endswith(".svg"):
            errors.append(f"{prefix}: link does not target an SVG")
        if href != src:
            errors.append(f"{prefix}: link and image target differ")
        if link.get("target") != "_blank":
            errors.append(f"{prefix}: link must open in a new tab")
        if not {"noopener", "noreferrer"}.issubset(rel):
            errors.append(f"{prefix}: link is missing noopener/noreferrer")
        if not (image.get("alt") or "").strip():
            errors.append(f"{prefix}: image alt text is empty")
        if diagram["action"] is not True:
            errors.append(f"{prefix}: visible full-size action is missing")

    return errors


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {Path(sys.argv[0]).name} HTML_FILE|- CSS_FILE", file=sys.stderr)
        return 2

    errors = validate(sys.argv[1], sys.argv[2])
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {EXPECTED_DIAGRAMS} diagrams link to their full-size SVGs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
