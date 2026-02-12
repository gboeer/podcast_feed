#!/usr/bin/env python3
"""Generate an RSS feed for ARD Audiothek shows.

Usage:
    python ardaudiothek_rss.py --show 10777871 --latest 10

Run as a local web server:
    python ardaudiothek_rss.py --serve --port 8000
    # then open http://localhost:8000/?show=10777871&latest=10
"""

from __future__ import annotations

import argparse
import sys
from html import escape

from feed_service import generate_feed, parse_and_validate
from rss_server import serve


def escape_string(value: object) -> str:
    return escape(str(value), quote=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate ARD Audiothek RSS feed")
    parser.add_argument("--show", type=str, help="Show ID (numeric)")
    parser.add_argument("--latest", type=str, default=None, help="Latest N episodes")
    parser.add_argument("--self-link", default="//localhost/ardaudiothek-rss.py", help="Atom self link")
    parser.add_argument("--serve", action="store_true", help="Run HTTP server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    args = parser.parse_args()

    if args.serve:
        serve(args.host, args.port)
        return 0

    try:
        show_id, latest = parse_and_validate(args.show, args.latest)
    except ValueError as exc:
        print(f"<error>{escape_string(exc)}</error>", file=sys.stderr)
        return 2

    rss_xml = generate_feed(show_id, latest, args.self_link)
    print(rss_xml)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
