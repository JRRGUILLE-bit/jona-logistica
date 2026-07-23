#!/usr/bin/env python3
"""Apply deterministic visual QA fixes across the static site."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_SOCIAL = "https://jrrguille-bit.github.io/jona-logistica/social-preview-jona-1200x630.jpg"
NEW_SOCIAL = "https://jrrguille-bit.github.io/jona-logistica/card.png?v=1"
PAGES = [
    Path("index.html"),
    Path("404.html"),
    Path("clima/index.html"),
    Path("movilidad/index.html"),
    Path("supermercados/index.html"),
    Path("docs/index.html"),
    Path("apps/index.html"),
    Path("discord/index.html"),
]


def write_if_changed(path: Path, text: str) -> None:
    target = ROOT / path
    old = target.read_text(encoding="utf-8")
    if old != text:
        target.write_text(text, encoding="utf-8", newline="\n")
        print(f"visual QA fixed: {path}")


def fix_page(path: Path) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    prefix = "" if path.parent == Path(".") else "../"

    text = text.replace(OLD_SOCIAL, NEW_SOCIAL)
    text = text.replace(
        '<meta property="og:image:type" content="image/jpeg">',
        '<meta property="og:image:type" content="image/png">',
    )

    if "visual-qa.css" not in text:
        stylesheet = f'<link rel="stylesheet" href="{prefix}visual-qa.css?v=20260723-1">\n'
        text = text.replace("</head>", stylesheet + "</head>", 1)

    write_if_changed(path, text)


def fix_worker() -> None:
    path = Path("service-worker.js")
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    text = text.replace("./social-preview-jona-1200x630.jpg", "./card.png?v=1")
    if "./visual-qa.css?v=20260723-1" not in text:
        marker = "  './site-touchup.css?v=20260723-2',"
        if marker in text:
            text = text.replace(marker, marker + "\n  './visual-qa.css?v=20260723-1',", 1)
        else:
            marker = "  './site-touchup.css?v=20260723-1',"
            text = text.replace(marker, marker + "\n  './visual-qa.css?v=20260723-1',", 1)
    write_if_changed(path, text)


def fix_qa_defaults() -> None:
    path = Path("scripts/qa_apply.py")
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    text = text.replace(
        'SOCIAL = BASE + "social-preview-jona-1200x630.jpg"',
        'SOCIAL = BASE + "card.png?v=1"',
    )
    write_if_changed(path, text)


for page in PAGES:
    fix_page(page)
fix_worker()
fix_qa_defaults()
