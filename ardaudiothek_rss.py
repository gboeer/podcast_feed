#!/usr/bin/env python3
"""Generate an RSS feed for ARD Audiothek shows.

This is a Python rebuild of the provided PHP implementation.

Usage:
    python ardaudiothek_rss.py --show 10777871 --latest 10

Run as a local web server:
    python ardaudiothek_rss.py --serve --port 8000
    # then open http://localhost:8000/?show=10777871&latest=10
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET


MAX_INT_32 = 2_147_483_647
GRAPHQL_URL = "https://api.ardaudiothek.de/graphql"


def get_file_length(url: str) -> int:
    """Fetch `Content-Length` for a remote resource, mirroring the PHP behavior."""
    req = Request(url, method="HEAD")
    try:
        with urlopen(req, timeout=20) as response:
            content_length = response.headers.get("Content-Length")
    except (HTTPError, URLError, ValueError):
        return -1

    try:
        return int(content_length) if content_length is not None else -1
    except ValueError:
        return -1


def get_show_json(show_id: int) -> dict[str, Any]:
    """Equivalent to the PHP getShowJson() helper."""
    url = f"https://api.ardaudiothek.de/programsets/{show_id}"
    req = Request(url, method="GET")
    with urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["data"]["programSet"]


def get_show_json_graphql(show_id: int, latest: int) -> dict[str, Any]:
    """Equivalent to the PHP getShowJsonGraphql() helper."""
    query = (
        "{"
        f"programSet(id:{show_id})"
        "{title,path,synopsis,sharingUrl,image{url,url1X1,},"
        f"items(orderBy:PUBLISH_DATE_DESC,filter:{{isPublished:{{equalTo:true}}}}first:{latest})"
        "{nodes{title,summary,synopsis,sharingUrl,"
        "publicationStartDateAndTime:publishDate,url,episodeNumber,duration,"
        "image{url,url1X1,},isPublished,audios{url,downloadUrl,size,mimeType,}}}}"
        "}"
    )
    body = json.dumps({"query": query}).encode("utf-8")
    req = Request(
        GRAPHQL_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    return payload["data"]["programSet"]


def escape_string(value: Any) -> str:
    """Equivalent to htmlspecialchars(..., ENT_QUOTES, 'UTF-8')."""
    return escape(str(value), quote=True)


def _format_rss_pubdate(iso_dt: str) -> str:
    dt = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return format_datetime(dt)


def _replace_width(url_template: str, width: str = "448") -> str:
    return url_template.replace("{width}", width)


def build_rss_xml(show: dict[str, Any], self_link: str) -> str:
    rss = ET.Element(
        "rss",
        {
            "xmlns:atom": "http://www.w3.org/2005/Atom",
            "xmlns:media": "http://search.yahoo.com/mrss/",
            "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
            "version": "2.0",
        },
    )
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = show.get("title", "")
    ET.SubElement(channel, "link").text = show.get("sharingUrl", "")

    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = _replace_width(show.get("image", {}).get("url1X1", ""))
    ET.SubElement(image, "title").text = show.get("title", "")
    ET.SubElement(image, "link").text = f"https://www.ardaudiothek.de{show.get('path', '')}"

    ET.SubElement(channel, "description").text = show.get("synopsis", "")
    ET.SubElement(
        channel,
        "{http://www.w3.org/2005/Atom}link",
        {"href": self_link, "rel": "self", "type": "application/rss+xml"},
    )

    for node in show.get("items", {}).get("nodes", []):
        item = ET.SubElement(channel, "item")
        audios = node.get("audios") or []
        primary_audio = audios[0] if audios else {}

        audio_url = primary_audio.get("url", "")
        download_url = primary_audio.get("downloadUrl", "")
        duration = int(node.get("duration") or 0)
        length = get_file_length(audio_url) if audio_url else -1

        ET.SubElement(item, "title").text = node.get("title", "")
        ET.SubElement(item, "description").text = node.get("synopsis", "")
        ET.SubElement(item, "guid").text = node.get("sharingUrl", "")
        ET.SubElement(item, "link").text = node.get("sharingUrl", "")
        ET.SubElement(
            item,
            "enclosure",
            {"url": audio_url, "length": str(length), "type": "audio/mpeg"},
        )
        ET.SubElement(
            item,
            "{http://search.yahoo.com/mrss/}content",
            {
                "url": download_url,
                "medium": "audio",
                "duration": str(duration),
                "type": "audio/mpeg",
            },
        )

        publish_date = node.get("publicationStartDateAndTime")
        if publish_date:
            ET.SubElement(item, "pubDate").text = _format_rss_pubdate(publish_date)
        ET.SubElement(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}duration").text = str(duration)

        item_image_url = _replace_width(node.get("image", {}).get("url1X1", ""))
        item_image = ET.SubElement(item, "image")
        ET.SubElement(item_image, "url").text = item_image_url
        ET.SubElement(item_image, "title").text = show.get("title", "")
        ET.SubElement(
            item,
            "{http://www.itunes.com/dtds/podcast-1.0.dtd}image",
            {"href": item_image_url},
        )

    xml = ET.tostring(rss, encoding="utf-8", xml_declaration=False)
    return xml.decode("utf-8")


def parse_and_validate(show_raw: str | None, latest_raw: str | None) -> tuple[int, int]:
    if show_raw is None or not show_raw.isdigit():
        raise ValueError('Invalid "show" parameter')

    latest = MAX_INT_32 if latest_raw is None else int(latest_raw) if latest_raw.isdigit() else -1
    if latest < 0:
        raise ValueError('Invalid "latest" parameter')

    return int(show_raw), latest


def generate_feed(show_id: int, latest: int, self_link: str) -> str:
    show = get_show_json_graphql(show_id, latest)
    return build_rss_xml(show, self_link)


class RSSHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        show_raw = params.get("show", [None])[0]
        latest_raw = params.get("latest", [None])[0]

        try:
            show_id, latest = parse_and_validate(show_raw, latest_raw)
        except ValueError as exc:
            self.send_response(400)
            self.send_header("Content-Type", "text/xml; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<error>{escape_string(exc)}</error>".encode("utf-8"))
            return

        host = self.headers.get("Host", "localhost")
        self_link = f"//{host}{parsed.path}?{urlencode({'show': show_id, 'latest': latest})}"

        try:
            rss_xml = generate_feed(show_id, latest, self_link)
        except Exception as exc:  # pragma: no cover
            self.send_response(502)
            self.send_header("Content-Type", "text/xml; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<error>{escape_string(exc)}</error>".encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/xml; charset=utf-8")
        self.end_headers()
        self.wfile.write(rss_xml.encode("utf-8"))


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
        server = ThreadingHTTPServer((args.host, args.port), RSSHandler)
        print(f"Serving on http://{args.host}:{args.port}")
        server.serve_forever()
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
