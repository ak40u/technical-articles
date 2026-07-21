#!/usr/bin/env python3
"""Verify the bilingual Hugo build against the GitHub Pages URL contract."""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


PAGE_PAIRS = (
    ("", "en/"),
    ("about/", "en/about/"),
    ("articles/", "en/articles/"),
    ("articles/ai-tech-teams-workflow/", "en/articles/ai-tech-teams-workflow/"),
    ("articles/autonomous-digital-employee/", "en/articles/autonomous-digital-employee/"),
)
EN_DIAGRAMS = (
    "en/articles/autonomous-digital-employee/hypothesis-pipeline.svg",
    "en/articles/autonomous-digital-employee/system-architecture.svg",
    "en/articles/autonomous-digital-employee/autonomy-loop.svg",
)
RU_DIAGRAMS = tuple(path.removeprefix("en/") for path in EN_DIAGRAMS)
MERMAID_HEADINGS = {
    "en/articles/autonomous-digital-employee/hypothesis-pipeline.svg": (
        "1 · DESIGN",
        "2 · PROOF",
        "3 · MONEY",
    ),
    "en/articles/autonomous-digital-employee/autonomy-loop.svg": (
        "1 · SENSE",
        "2 · DECIDE",
        "3 · LEARN",
    ),
}
EXPECTED_ARTICLE_TITLES = {
    "articles/autonomous-digital-employee/": "Как я создал автономного цифрового сотрудника",
    "en/articles/autonomous-digital-employee/": "How I Built an Autonomous Digital Employee",
}
CYRILLIC = re.compile(r"[А-Яа-яЁё]")
TELEGRAM_URL = "https://t.me/sueta_localna"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = ""
        self.canonical = ""
        self.hreflang: dict[str, str] = {}
        self.og_locale = ""
        self.og_image = ""
        self.rss = ""
        self.language_options: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.telegram_ctas: list[dict[str, str]] = []
        self.images: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        classes = set(attrs.get("class", "").split())

        if tag == "html":
            self.html_lang = attrs.get("lang", "")
        elif tag == "link":
            rel = set(attrs.get("rel", "").split())
            if "canonical" in rel:
                self.canonical = attrs.get("href", "")
            elif "alternate" in rel and attrs.get("hreflang"):
                self.hreflang[attrs["hreflang"]] = attrs.get("href", "")
            elif "alternate" in rel and attrs.get("type") == "application/rss+xml":
                self.rss = attrs.get("href", "")
        elif tag == "meta":
            if attrs.get("property") == "og:locale":
                self.og_locale = attrs.get("content", "")
            elif attrs.get("property") == "og:image":
                self.og_image = attrs.get("content", "")
        elif tag == "a":
            self.links.append(attrs)
            if "language-option" in classes:
                self.language_options.append(attrs)
            if "telegram-cta" in classes:
                self.telegram_ctas.append(attrs)
        elif tag == "img":
            self.images.append(attrs.get("src", ""))

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.text_parts.append(data)


def page_file(public: Path, route: str) -> Path:
    return public / route / "index.html" if route else public / "index.html"


def parse_page(path: Path) -> tuple[PageParser, str]:
    text = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(text)
    return parser, text


def expected_url(base_url: str, route: str) -> str:
    return f"{base_url}{route}"


def validate_telegram_ctas(public: Path) -> list[str]:
    errors: list[str] = []
    article_roots = ((public / "articles", True), (public / "en" / "articles", False))

    for article_root, should_have_cta in article_roots:
        if not article_root.is_dir():
            continue
        for path in sorted(article_root.rglob("index.html")):
            if path.parent == article_root:
                continue
            parser, _ = parse_page(path)
            label = path.relative_to(public)
            telegram_links = [link for link in parser.links if link.get("href") == TELEGRAM_URL]
            if should_have_cta:
                if len(telegram_links) != 1:
                    errors.append(f"{label}: expected exactly one link to {TELEGRAM_URL}")
                if len(parser.telegram_ctas) != 1:
                    errors.append(f"{label}: expected exactly one Telegram CTA")
                    continue
                cta = parser.telegram_ctas[0]
                if cta.get("href") != TELEGRAM_URL:
                    errors.append(f"{label}: incorrect Telegram CTA URL {cta.get('href')!r}")
                if cta.get("target") != "_blank":
                    errors.append(f"{label}: Telegram CTA must open in a new tab")
                rel = set(cta.get("rel", "").split())
                if not {"noopener", "noreferrer"}.issubset(rel):
                    errors.append(f"{label}: Telegram CTA has unsafe rel {cta.get('rel')!r}")
            elif telegram_links or parser.telegram_ctas:
                errors.append(f"{label}: English article contains the Russian Telegram link")

    for route in ("", "about/", "articles/"):
        path = page_file(public, route)
        if not path.is_file():
            continue
        parser, _ = parse_page(path)
        telegram_links = [link for link in parser.links if link.get("href") == TELEGRAM_URL]
        if telegram_links or parser.telegram_ctas:
            errors.append(f"{route or '/'}: non-article page contains the Telegram link")

    return errors


def validate_page(
    public: Path,
    base_url: str,
    base_path: str,
    route: str,
    peer_route: str,
    locale: str,
    og_locale: str,
) -> list[str]:
    errors: list[str] = []
    path = page_file(public, route)
    if not path.is_file():
        return [f"missing page: {path.relative_to(public)}"]

    parser, _ = parse_page(path)
    label = route or "/"
    peer_locale = "en-US" if locale == "ru" else "ru"
    expected_hreflang = {
        locale: expected_url(base_url, route),
        peer_locale: expected_url(base_url, peer_route),
    }
    expected_switch = {
        f"{base_path}{route}",
        f"{base_path}{peer_route}",
    }

    if parser.html_lang != locale:
        errors.append(f"{label}: html lang is {parser.html_lang!r}, expected {locale!r}")
    if parser.canonical != expected_url(base_url, route):
        errors.append(f"{label}: incorrect canonical {parser.canonical!r}")
    if parser.hreflang != expected_hreflang:
        errors.append(f"{label}: incorrect hreflang map {parser.hreflang!r}")
    if parser.og_locale != og_locale:
        errors.append(f"{label}: incorrect og:locale {parser.og_locale!r}")

    expected_rss = expected_url(base_url, "index.xml" if locale == "ru" else "en/index.xml")
    if parser.rss != expected_rss:
        errors.append(f"{label}: incorrect RSS discovery {parser.rss!r}")

    switch_hrefs = {option.get("href", "") for option in parser.language_options}
    if switch_hrefs != expected_switch:
        errors.append(f"{label}: incorrect language switch targets {switch_hrefs!r}")
    active = [option for option in parser.language_options if option.get("aria-current") == "page"]
    if len(active) != 1 or active[0].get("lang") != locale:
        errors.append(f"{label}: active language is missing or incorrect")

    english_text = " ".join(parser.text_parts).replace('Павел Волков', 'Pavel Volkov')
    if locale == "en-US" and CYRILLIC.search(english_text):
        errors.append(f"{label}: English HTML contains Cyrillic text")

    expected_title = EXPECTED_ARTICLE_TITLES.get(route)
    if expected_title and expected_title not in parser.text_parts:
        errors.append(f"{label}: expected article title is missing")

    if route.endswith("en/articles/autonomous-digital-employee/"):
        expected_prefix = f"{base_path}en/articles/autonomous-digital-employee/"
        diagram_sources = [src for src in parser.images if src.endswith(".svg")]
        if len(diagram_sources) != 3 or any(not src.startswith(expected_prefix) for src in diagram_sources):
            errors.append(f"{label}: English diagrams do not use the English page bundle")

    return errors


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {Path(sys.argv[0]).name} PUBLIC_DIR BASE_URL", file=sys.stderr)
        return 2

    public = Path(sys.argv[1])
    base_url = sys.argv[2].rstrip("/") + "/"
    base_path = urlparse(base_url).path
    errors: list[str] = []

    for ru_route, en_route in PAGE_PAIRS:
        errors.extend(validate_page(public, base_url, base_path, ru_route, en_route, "ru", "ru_RU"))
        errors.extend(validate_page(public, base_url, base_path, en_route, ru_route, "en-US", "en_US"))

    errors.extend(validate_telegram_ctas(public))

    expected_assets = (
        *RU_DIAGRAMS,
        *EN_DIAGRAMS,
        "og/ai-tech-teams-workflow-hero.png",
        "og/ai-tech-teams-workflow-hero-en.png",
        "og/autonomous-digital-employee-hero.png",
        "og/autonomous-digital-employee-hero-en.png",
        "index.xml",
        "en/index.xml",
        "llms.txt",
        "en/llms.txt",
        "robots.txt",
        "sitemap.xml",
    )
    for relative in expected_assets:
        path = public / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty asset: {relative}")

    for relative in (*RU_DIAGRAMS, *EN_DIAGRAMS):
        path = public / relative
        if path.is_file():
            try:
                ET.parse(path)
            except ET.ParseError as exc:
                errors.append(f"invalid SVG {relative}: {exc}")
            svg_text = path.read_text(encoding="utf-8")
            if relative.startswith("en/") and CYRILLIC.search(svg_text):
                errors.append(f"English SVG contains Cyrillic text: {relative}")
            if relative in MERMAID_HEADINGS:
                for heading in MERMAID_HEADINGS[relative]:
                    if heading not in svg_text:
                        errors.append(f"{relative}: missing Mermaid heading {heading!r}")
                font_rule = ".cluster-label{font-family:Arial,Helvetica,sans-serif!important;}"
                if font_rule not in svg_text:
                    errors.append(f"{relative}: missing explicit cluster-label font rule")

    text_expectations = {
        "llms.txt": ("# Технические статьи", "## Статьи"),
        "en/llms.txt": ("# Technical Articles", "## Articles"),
        "index.xml": ("Технические статьи",),
        "en/index.xml": ("Technical Articles",),
    }
    for relative, fragments in text_expectations.items():
        path = public / relative
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for fragment in fragments:
                if fragment not in text:
                    errors.append(f"{relative}: missing {fragment!r}")

    robots = public / "robots.txt"
    if robots.is_file() and f"Sitemap: {base_url}sitemap.xml" not in robots.read_text(encoding="utf-8"):
        errors.append("robots.txt does not point to the root sitemap")

    sitemap = public / "sitemap.xml"
    if sitemap.is_file():
        sitemap_text = sitemap.read_text(encoding="utf-8")
        if base_url not in sitemap_text or f"{base_url}en/" not in sitemap_text:
            errors.append("sitemap.xml does not expose both language sites")

    page_og = {
        "": "og/ai-tech-teams-workflow-hero.png",
        "about/": "og/ai-tech-teams-workflow-hero.png",
        "articles/": "og/ai-tech-teams-workflow-hero.png",
        "articles/ai-tech-teams-workflow/": "og/ai-tech-teams-workflow-hero.png",
        "articles/autonomous-digital-employee/": "og/autonomous-digital-employee-hero.png",
        "en/": "og/ai-tech-teams-workflow-hero-en.png",
        "en/about/": "og/ai-tech-teams-workflow-hero-en.png",
        "en/articles/": "og/ai-tech-teams-workflow-hero-en.png",
        "en/articles/ai-tech-teams-workflow/": "og/ai-tech-teams-workflow-hero-en.png",
        "en/articles/autonomous-digital-employee/": "og/autonomous-digital-employee-hero-en.png",
    }
    for route, image in page_og.items():
        path = page_file(public, route)
        if path.is_file():
            parser, _ = parse_page(path)
            if parser.og_image != expected_url(base_url, image):
                errors.append(f"{route or '/'}: incorrect OG image {parser.og_image!r}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {len(PAGE_PAIRS)} RU/EN page pairs and all bilingual assets are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
