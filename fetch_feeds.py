#!/usr/bin/env python3
"""Fetch RSS feeds for all podcasts listed in podcasts.json and store them under feeds/."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from ardaudiothek_api import get_file_length, get_show_json_graphql
from feed_service import parse_and_validate
from rss_xml import build_rss_xml


PODCASTS_FILE = Path(__file__).parent / "podcasts.json"
FEEDS_DIR = Path(__file__).parent / "feeds"


def _slug(name: str) -> str:
    """Convert a podcast name to a safe filename stem."""
    return "".join(c if c.isalnum() else "_" for c in name).strip("_").lower()


def _feed_base_url() -> str:
    """Base URL used for atom:self links in generated RSS files."""
    return os.getenv("FEED_BASE_URL", "http://localhost:8000/feeds").rstrip("/")


def main() -> int:
    podcasts = json.loads(PODCASTS_FILE.read_text(encoding="utf-8"))
    feed_base_url = _feed_base_url()

    FEEDS_DIR.mkdir(exist_ok=True)

    errors: list[str] = []
    for entry in podcasts:
        name = entry["name"]
        show_id = str(entry["show_id"])
        latest = entry.get("latest")

        print(f"Fetching: {name} (show_id={show_id}, latest={latest})")
        try:
            request = parse_and_validate(show_id, str(latest) if latest is not None else None)
            show = get_show_json_graphql(request.show_id, request.latest)
            self_link = f"{feed_base_url}/{_slug(name)}.xml"
            xml = build_rss_xml(show, self_link, get_file_length=get_file_length)
            source_url = show.get("sharingUrl", "")
            if source_url:
                entry["source_url"] = source_url
        except Exception as exc:
            msg = f"  ERROR fetching {name}: {exc}"
            print(msg, file=sys.stderr)
            errors.append(msg)
            continue

        out_path = FEEDS_DIR / f"{_slug(name)}.xml"
        out_path.write_text(xml, encoding="utf-8")
        print(f"  Saved -> {out_path.relative_to(Path(__file__).parent)}")

    PODCASTS_FILE.write_text(json.dumps(podcasts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated -> {PODCASTS_FILE.name}")

    if errors:
        print(f"\n{len(errors)} feed(s) failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
