#!/usr/bin/env python3
"""Validate podcasts.json: JSON syntax plus the fields fetch_feeds.py relies on."""

from __future__ import annotations

import json
import sys

from feed_files import PODCASTS_FILE, ROOT, feed_filename
from feed_service import parse_and_validate


def validate(text: str) -> list[str]:
    try:
        podcasts = json.loads(text)
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc.msg} (line {exc.lineno}, column {exc.colno})"]

    if not isinstance(podcasts, list) or not podcasts:
        return ["top level must be a non-empty list of podcast entries"]

    errors: list[str] = []
    # Feed filename -> entry that owns it, to catch the same show listed twice.
    seen_files: dict[str, str] = {}

    for index, entry in enumerate(podcasts):
        where = f"entry {index}"
        if not isinstance(entry, dict):
            errors.append(f"{where}: must be an object")
            continue

        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{where}: 'name' must be a non-empty string")
        else:
            where = f"entry {index} ({name!r})"

        show_id = entry.get("show_id")
        latest = entry.get("latest")
        if not isinstance(show_id, str):
            errors.append(f"{where}: 'show_id' must be a string")
        elif latest is not None and (isinstance(latest, bool) or not isinstance(latest, int)):
            errors.append(f"{where}: 'latest' must be a positive integer if set")
        else:
            try:
                request = parse_and_validate(show_id, str(latest) if latest is not None else None)
            except ValueError as exc:
                errors.append(f"{where}: {exc}")
            else:
                filename = feed_filename(request.show_id)
                if filename in seen_files:
                    errors.append(f"{where}: same show as {seen_files[filename]}")
                else:
                    seen_files[filename] = where

    return errors


def main() -> int:
    errors = validate(PODCASTS_FILE.read_text(encoding="utf-8"))
    name = PODCASTS_FILE.relative_to(ROOT)
    if errors:
        for error in errors:
            print(f"{name}: {error}", file=sys.stderr)
        return 1
    print(f"{name}: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
