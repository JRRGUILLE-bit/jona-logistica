#!/usr/bin/env python3
"""Apply deterministic QA fixes to the static site."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://jrrguille-bit.github.io/jona-logistica/"
SOCIAL = BASE + "card.png?v=1"
PAGES = [
    Path("index.html"), Path("404.html"), Path("clima/index.html"),
    Path("movilidad/index.html"), Path("supermercados/index.html"),
    Path("docs/index.html"), Path("apps/index.html"), Path("discord/index.html"),
]


def save(path: Path, text: str) -> None:
    target = ROOT / path
    old = target.read_text(encoding="utf-8")
    if old != text:
        target.write_text(text, encoding="utf-8", newline="\n")
        print(f"fixed: {path}")


def blank_rel(tag: str) -> str:
    if not re.search(r'target=["\']_blank["\']', tag, re.I):
        return tag
    match = re.search(r'rel=(["\'])(.*?)\1', tag, re.I)
    if not match:
        return tag[:-1] + ' rel="noopener noreferrer">'
    tokens = match.group(2).split()
    for token in ("noopener", "noreferrer"):
        if token not in tokens:
            tokens.append(token)
    replacement = f'rel={match.group(1)}{" ".join(tokens)}{match.group(1)}'
    return tag[:match.start()] + replacement + tag[match.end():]


def ensure_social(text: str) -> str:
    title_match = re.search(r"<title>(.*?)</title>", text, re.S)
    desc_match = re.search(r'<meta name="description" content="([^"]*)">', text)
    canonical_match = re.search(r'<link rel="canonical" href="([^"]*)">', text)
    if not title_match:
        return text
    title = re.sub(r"\s+", " ", title_match.group(1)).strip()
    desc = desc_match.group(1) if desc_match else "Base de operaciones del rodaje de Jona tenía 15 años."
    canonical = canonical_match.group(1) if canonical_match else BASE
    if 'property="og:title"' not in text:
        block = (
            f'<meta property="og:title" content="{title}">\n'
            f'<meta property="og:description" content="{desc}">\n'
            '<meta property="og:type" content="website">\n'
            f'<meta property="og:url" content="{canonical}">\n'
        )
        text = text.replace(title_match.group(0), block + title_match.group(0), 1)
    if 'property="og:image"' not in text:
        block = (
            f'<meta property="og:image" content="{SOCIAL}">\n'
            f'<meta property="og:image:secure_url" content="{SOCIAL}">\n'
            '<meta property="og:image:type" content="image/jpeg">\n'
            '<meta property="og:image:width" content="1200">\n'
            '<meta property="og:image:height" content="630">\n'
            f'<meta property="og:image:alt" content="{title}">\n'
        )
        marker = re.search(r'<meta property="og:url"[^>]*>\s*', text)
        if marker:
            text = text[:marker.end()] + block + text[marker.end():]
    if 'name="twitter:card"' not in text:
        block = (
            '<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:title" content="{title}">\n'
            f'<meta name="twitter:description" content="{desc}">\n'
            f'<meta name="twitter:image" content="{SOCIAL}">\n'
            f'<meta name="twitter:image:alt" content="{title}">\n'
        )
        text = text.replace(title_match.group(0), block + title_match.group(0), 1)
    return text


def fix_page(path: Path) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    head, tail = text.split("</head>", 1)
    head = head.replace("\\n<", "\n<")
    text = head + "</head>" + tail
    prefix = "" if path.parent == Path(".") else "../"

    if 'name="color-scheme"' not in text:
        common = (
            '<meta name="color-scheme" content="dark">\n'
            '<meta name="mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
            '<meta name="apple-mobile-web-app-title" content="Jona Ops">\n'
            '<meta name="format-detection" content="telephone=no">\n'
        )
        match = re.search(r'<meta name="theme-color"[^>]*>\s*', text)
        if match:
            text = text[:match.end()] + common + text[match.end():]

    if 'android-chrome-192x192.png' not in text:
        match = re.search(r'<link rel="apple-touch-icon"[^>]*>\s*', text)
        if match:
            icon = f'<link rel="icon" type="image/png" sizes="192x192" href="{prefix}android-chrome-192x192.png">\n'
            text = text[:match.end()] + icon + text[match.end():]

    if 'rel="manifest"' not in text:
        text = text.replace("</head>", f'<link rel="manifest" href="{prefix}manifest.webmanifest">\n</head>', 1)

    if re.search(r'<script[^>]+src=["\'][^"\']*offline\.js', text):
        text = re.sub(
            r'(<script[^>]+src=["\'])[^"\']*offline\.js(?:\?v=\d+)?(["\'])',
            rf'\1{prefix}offline.js?v=3\2', text, count=1,
        )
    else:
        text = text.replace("</head>", f'<script defer src="{prefix}offline.js?v=3"></script>\n</head>', 1)

    if path == Path("supermercados/index.html"):
        text = text.replace('<div class="page">', '<main id="main-content" class="page">', 1)
        text = text.replace('<main class="panel">', '<section class="panel">', 1)
        text = text.replace('</div></main>', '</div></section>', 1)
        text = text.replace('</footer>\n</div>\n<script>', '</footer>\n</main>\n<script>', 1)
        text = text.replace('<nav class="tabs">', '<nav class="tabs" role="tablist" aria-label="Filtrar lugares">', 1)
        text = text.replace('<button class="tab active" data-filter="Todos">', '<button type="button" class="tab active" role="tab" aria-selected="true" data-filter="Todos">', 1)
        for value in ("Supermercado", "Almacén", "Farmacia"):
            text = text.replace(
                f'<button class="tab" data-filter="{value}">',
                f'<button type="button" class="tab" role="tab" aria-selected="false" data-filter="{value}">', 1,
            )
        old = "document.querySelectorAll('.tab').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));btn.classList.add('active');render(btn.dataset.filter)}));render();"
        new = "document.querySelectorAll('.tab').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.tab').forEach(b=>{b.classList.remove('active');b.setAttribute('aria-selected','false')});btn.classList.add('active');btn.setAttribute('aria-selected','true');render(btn.dataset.filter)}));render();"
        text = text.replace(old, new)

    if 'id="main-content"' not in text:
        text = re.sub(r"<main(\s+)", r'<main id="main-content"\1', text, count=1)

    text = ensure_social(text)
    text = re.sub(r"<a\b[^>]*>", lambda m: blank_rel(m.group(0)), text, flags=re.I)
    save(path, text)


def fix_offline() -> None:
    path = ROOT / "offline.js"
    text = path.read_text(encoding="utf-8")
    marker = "  document.head.appendChild(style);\n"
    injection = """

  const mainContent = document.querySelector('main');
  if (mainContent) {
    if (!mainContent.id) mainContent.id = 'main-content';
    if (!document.querySelector('.skip-link')) {
      const skipLink = document.createElement('a');
      skipLink.className = 'skip-link';
      skipLink.href = `#${mainContent.id}`;
      skipLink.textContent = 'Saltar al contenido';
      document.body.prepend(skipLink);
    }
  }
"""
    if "const mainContent = document.querySelector('main');" not in text:
        text = text.replace(marker, marker + injection, 1)
    save(Path("offline.js"), text)


def fix_manifest() -> None:
    path = Path("manifest.webmanifest")
    data = json.loads((ROOT / path).read_text(encoding="utf-8"))
    data["prefer_related_applications"] = False
    for icon in data.get("icons", []):
        if str(icon.get("src", "")).lower().endswith(".svg"):
            icon["sizes"] = "any"
    for shortcut in data.get("shortcuts", []):
        for icon in shortcut.get("icons", []):
            if str(icon.get("src", "")).lower().endswith(".svg"):
                icon["sizes"] = "any"
    save(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def fix_worker() -> None:
    path = Path("service-worker.js")
    text = (ROOT / path).read_text(encoding="utf-8")
    text = re.sub(r'(const CACHE_NAME = `\$\{CACHE_PREFIX\})v\d+(`;)', r'\1v5\2', text)
    text = text.replace("./offline.js?v=2", "./offline.js?v=3")
    if "./app-icon-512.svg" not in text:
        text = text.replace("  './android-chrome-192x192.png',", "  './android-chrome-192x192.png',\n  './app-icon-512.svg',")
    save(path, text)


for page in PAGES:
    fix_page(page)
fix_offline()
fix_manifest()
fix_worker()
