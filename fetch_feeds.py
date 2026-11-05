#!/usr/bin/env python3
"""Fetch RSS feeds for all podcasts listed in podcasts.json and store them under feeds/."""

from __future__ import annotations

import json
import os
import sys

from ardaudiothek_api import get_file_length, get_show_json_graphql
from feed_files import FEEDS_DIR, PODCASTS_FILE, ROOT, feed_base_url, feed_slug
from feed_service import parse_and_validate
from rss_xml import build_rss_xml


def _escape_annotation(value: str, *, is_property: bool = False) -> str:
    """Escape text for a GitHub Actions workflow command (e.g. ::warning::)."""
    value = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    if is_property:
        value = value.replace(":", "%3A").replace(",", "%2C")
    return value


def main() -> int:
    podcasts = json.loads(PODCASTS_FILE.read_text(encoding="utf-8"))
    base_url = feed_base_url()

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
            self_link = f"{base_url}/{feed_slug(name)}.xml"
            xml = build_rss_xml(show, self_link, get_file_length=get_file_length)
            source_url = show.get("sharingUrl", "")
            if source_url:
                entry["source_url"] = source_url
        except Exception as exc:
            msg = f"  ERROR fetching {name}: {exc}"
            print(msg, file=sys.stderr)
            if os.getenv("GITHUB_ACTIONS") == "true":
                # Surface the failure as an annotation on the workflow run page.
                title = _escape_annotation(f"Feed failed: {name}", is_property=True)
                print(f"::warning title={title}::{_escape_annotation(str(exc))}")
            errors.append(msg)
            continue

        out_path = FEEDS_DIR / f"{feed_slug(name)}.xml"
        out_path.write_text(xml, encoding="utf-8")
        print(f"  Saved -> {out_path.relative_to(ROOT)}")

    PODCASTS_FILE.write_text(json.dumps(podcasts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated -> {PODCASTS_FILE.name}")

    if errors:
        print(f"\n{len(errors)} of {len(podcasts)} feed(s) failed.", file=sys.stderr)
        # Only fail the run if nothing was generated, so one broken show
        # doesn't block publishing the others.
        if len(errors) == len(podcasts):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
