#!/usr/bin/env python3
"""Fetch RSS feeds for all podcasts listed in podcasts.json and store them under feeds/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from feed_service import generate_feed, parse_and_validate


PODCASTS_FILE = Path(__file__).parent / "podcasts.json"
FEEDS_DIR = Path(__file__).parent / "feeds"


def _slug(name: str) -> str:
    """Convert a podcast name to a safe filename stem."""
    return "".join(c if c.isalnum() else "_" for c in name).strip("_").lower()


def main() -> int:
    podcasts = json.loads(PODCASTS_FILE.read_text(encoding="utf-8"))

    FEEDS_DIR.mkdir(exist_ok=True)

    errors: list[str] = []
    for entry in podcasts:
        name = entry["name"]
        show_id = str(entry["show_id"])
        latest = entry.get("latest")

        print(f"Fetching: {name} (show_id={show_id}, latest={latest})")
        try:
            request = parse_and_validate(show_id, str(latest) if latest is not None else None)
            self_link = f"//localhost/feeds/{_slug(name)}.xml"
            xml = generate_feed(request, self_link)
        except Exception as exc:
            msg = f"  ERROR fetching {name}: {exc}"
            print(msg, file=sys.stderr)
            errors.append(msg)
            continue

        out_path = FEEDS_DIR / f"{_slug(name)}.xml"
        out_path.write_text(xml, encoding="utf-8")
        print(f"  Saved -> {out_path.relative_to(Path(__file__).parent)}")

    if errors:
        print(f"\n{len(errors)} feed(s) failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
