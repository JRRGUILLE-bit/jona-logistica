#!/usr/bin/env python3
"""Translate MetSul headlines and excerpts from Portuguese to Spanish.

The weather collector remains independent from the translation engine. This
script runs immediately afterwards, stores a small translation memory in the
repository, and leaves the original Portuguese text available as a fallback.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
WEATHER_PATH = ROOT / "data" / "weather.json"
CACHE_PATH = ROOT / "data" / "metsul-translations.json"
SOURCE_CODE = "pt"
TARGET_CODE = "es"
PIVOT_CODE = "en"
MAX_CACHE_ENTRIES = 250


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def original_text(article: dict[str, Any], field: str) -> str:
    return str(
        article.get(f"{field}_pt")
        or article.get(f"{field}_original")
        or article.get(field)
        or ""
    ).strip()


def cache_key(title: str, excerpt: str) -> str:
    source = json.dumps(
        {"title": title, "excerpt": excerpt},
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def installed_pair(from_code: str, to_code: str) -> bool:
    import argostranslate.translate

    languages = argostranslate.translate.get_installed_languages()
    source = next((lang for lang in languages if lang.code == from_code), None)
    target = next((lang for lang in languages if lang.code == to_code), None)
    if source is None or target is None:
        return False
    try:
        source.get_translation(target)
        return True
    except Exception:
        return False


def install_pair(from_code: str, to_code: str, available: list[Any]) -> None:
    import argostranslate.package

    if installed_pair(from_code, to_code):
        return

    candidates = [
        package
        for package in available
        if package.from_code == from_code and package.to_code == to_code
    ]
    if not candidates:
        raise RuntimeError(f"Argos no ofrece el modelo {from_code} → {to_code}")

    package = sorted(candidates, key=lambda item: item.package_version)[-1]
    print(f"Installing Argos {from_code} → {to_code} model…")
    argostranslate.package.install_from_path(package.download())


def ensure_translation_engine() -> tuple[Callable[[str], str], str]:
    import argostranslate.package
    import argostranslate.translate

    if installed_pair(SOURCE_CODE, TARGET_CODE):
        return (
            lambda text: argostranslate.translate.translate(text, SOURCE_CODE, TARGET_CODE),
            "direct",
        )

    argostranslate.package.update_package_index()
    available = argostranslate.package.get_available_packages()

    direct_available = any(
        package.from_code == SOURCE_CODE and package.to_code == TARGET_CODE
        for package in available
    )
    if direct_available:
        install_pair(SOURCE_CODE, TARGET_CODE, available)
        route = "direct"
    else:
        install_pair(SOURCE_CODE, PIVOT_CODE, available)
        install_pair(PIVOT_CODE, TARGET_CODE, available)
        route = f"{SOURCE_CODE}-{PIVOT_CODE}-{TARGET_CODE}"

    def translate_text(text: str) -> str:
        return argostranslate.translate.translate(text, SOURCE_CODE, TARGET_CODE)

    # Fail during setup rather than halfway through the article list.
    probe = str(translate_text("Previsão do tempo") or "").strip()
    if not probe:
        raise RuntimeError("Argos se instaló pero no pudo traducir portugués a español")

    return translate_text, route


def safe_translate(translate_text: Callable[[str], str], text: str) -> str:
    if not text:
        return ""
    result = str(translate_text(text) or "").strip()
    # Guard against empty or pathological repetitive model output.
    if not result or len(result) > max(500, len(text) * 5):
        raise ValueError("La traducción automática produjo una salida inválida")
    return result


def translate_articles(
    articles: list[dict[str, Any]],
    entries: dict[str, dict[str, Any]],
    translate_text: Callable[[str], str],
    route: str,
) -> tuple[int, int]:
    translated_count = 0
    cached_count = 0

    for article in articles:
        title_pt = original_text(article, "title")
        excerpt_pt = original_text(article, "excerpt")
        key = cache_key(title_pt, excerpt_pt)
        cached = entries.get(key)

        if cached and cached.get("title_pt") == title_pt and cached.get("excerpt_pt") == excerpt_pt:
            title_es = str(cached.get("title_es") or title_pt)
            excerpt_es = str(cached.get("excerpt_es") or excerpt_pt)
            cached_count += 1
        else:
            title_es = safe_translate(translate_text, title_pt)
            excerpt_es = safe_translate(translate_text, excerpt_pt) if excerpt_pt else ""
            entries[key] = {
                "title_pt": title_pt,
                "excerpt_pt": excerpt_pt,
                "title_es": title_es,
                "excerpt_es": excerpt_es,
                "route": route,
            }
            translated_count += 1

        article.update(
            {
                "title_pt": title_pt,
                "excerpt_pt": excerpt_pt,
                "title": title_es or title_pt,
                "excerpt": excerpt_es or excerpt_pt,
                "language": "es",
                "original_language": "pt",
                "translation_status": "translated",
                "translation_engine": "Argos Translate",
                "translation_route": route,
            }
        )

    return translated_count, cached_count


def propagate_to_days(payload: dict[str, Any], source_articles: list[dict[str, Any]]) -> None:
    by_id = {str(article.get("id")): article for article in source_articles if article.get("id") is not None}
    by_url = {str(article.get("url")): article for article in source_articles if article.get("url")}

    for day in payload.get("days", []):
        translated: list[dict[str, Any]] = []
        for article in day.get("metsul_articles", []):
            match = by_id.get(str(article.get("id"))) or by_url.get(str(article.get("url")))
            translated.append(dict(match) if match else article)
        day["metsul_articles"] = translated


def prune_entries(entries: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if len(entries) <= MAX_CACHE_ENTRIES:
        return entries
    # JSON dictionaries preserve insertion order; retain the most recent items.
    return dict(list(entries.items())[-MAX_CACHE_ENTRIES:])


def main() -> int:
    payload = load_json(WEATHER_PATH, {})
    if not payload:
        print(f"No se encontró un weather.json válido en {WEATHER_PATH}", file=sys.stderr)
        return 0

    source = payload.setdefault("sources", {}).setdefault("metsul", {})
    articles = source.get("articles", [])
    if not articles:
        source["translation"] = {
            "status": "not-needed",
            "engine": "Argos Translate",
            "source_language": SOURCE_CODE,
            "target_language": TARGET_CODE,
        }
        write_json(WEATHER_PATH, payload)
        return 0

    cache = load_json(
        CACHE_PATH,
        {
            "schema_version": 1,
            "engine": "Argos Translate",
            "source_language": SOURCE_CODE,
            "target_language": TARGET_CODE,
            "entries": {},
        },
    )
    entries = cache.setdefault("entries", {})

    try:
        translate_text, route = ensure_translation_engine()
        translated_count, cached_count = translate_articles(
            articles, entries, translate_text, route
        )
        propagate_to_days(payload, articles)
        source["translation"] = {
            "status": "ok",
            "engine": "Argos Translate",
            "source_language": SOURCE_CODE,
            "target_language": TARGET_CODE,
            "route": route,
            "translated_now": translated_count,
            "from_cache": cached_count,
        }
        cache["entries"] = prune_entries(entries)
        write_json(CACHE_PATH, cache)
        print(
            f"MetSul: {translated_count} traducciones nuevas, "
            f"{cached_count} recuperadas del caché. Ruta: {route}."
        )
    except Exception as exc:
        # Translation is an enhancement: never erase or block weather data.
        source["translation"] = {
            "status": "fallback",
            "engine": "Argos Translate",
            "source_language": SOURCE_CODE,
            "target_language": TARGET_CODE,
            "error": str(exc),
        }
        print(f"MetSul translation fallback: {exc}", file=sys.stderr)

    write_json(WEATHER_PATH, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
