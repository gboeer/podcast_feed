from __future__ import annotations

from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

from feed_service import generate_feed, parse_and_validate


def escape_string(value: object) -> str:
    return escape(str(value), quote=True)


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


def serve(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), RSSHandler)
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()
