#!/usr/bin/env python3
"""Generate a simple GitHub Pages landing page for available podcast feeds."""

from __future__ import annotations

import html
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).parent
PODCASTS_FILE = ROOT / "podcasts.json"
PUBLIC_DIR = ROOT / "public"
INDEX_FILE = PUBLIC_DIR / "index.html"
TEMPLATE_FILE = ROOT / "templates" / "index.html"
TEMPLATE_CSS_FILE = ROOT / "templates" / "index.css"
OUTPUT_CSS_FILE = PUBLIC_DIR / "index.css"


def _slug(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name).strip("_").lower()


def _feed_base_url() -> str:
    return os.getenv("FEED_BASE_URL", "http://localhost:8000/feeds").rstrip("/")


def _build_index_html(podcasts: list[dict[str, object]], feed_base_url: str) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    items: list[str] = []

    for entry in podcasts:
        name = str(entry["name"])
        slug = _slug(name)
        feed_url = f"{feed_base_url}/{slug}.xml"
        escaped_name = html.escape(name)
        escaped_url = html.escape(feed_url)
        escaped_url_attr = html.escape(feed_url, quote=True)
        search_text = html.escape(f"{name} {feed_url}".lower(), quote=True)
        items.append(
            (
                f'<li data-search="{search_text}">'
                f"<strong>{escaped_name}</strong><br>"
                '<div class="feed-link-row">'
                f'<a href="{escaped_url}">{escaped_url}</a>'
                f'<button class="copy-btn" type="button" data-copy="{escaped_url_attr}" aria-label="Copy feed URL" title="Copy feed URL">'
                '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M16 1H6c-1.1 0-2 .9-2 2v12h2V3h10V1zm3 4H10c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h9c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H10V7h9v14z"/></svg>'
                "</button>"
                "</div>"
                "</li>"
            )
        )

    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    items_markup = "\n".join(items)
    return (
        template.replace("__FEED_ITEMS__", items_markup).replace("__GENERATED_AT__", generated_at)
    )


def main() -> int:
    podcasts = json.loads(PODCASTS_FILE.read_text(encoding="utf-8"))
    feed_base_url = _feed_base_url()

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(
        _build_index_html(podcasts, feed_base_url),
        encoding="utf-8",
    )
    shutil.copyfile(TEMPLATE_CSS_FILE, OUTPUT_CSS_FILE)
    print(f"Saved -> {INDEX_FILE.relative_to(ROOT)}")
    print(f"Saved -> {OUTPUT_CSS_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
