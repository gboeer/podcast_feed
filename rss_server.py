from __future__ import annotations

from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

from feed_service import generate_feed, parse_and_validate


def _xml_error(value: object) -> bytes:
    return f"<error>{escape(str(value), quote=True)}</error>".encode("utf-8")


class RSSHandler(BaseHTTPRequestHandler):
    def _send_xml(self, status: int, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/xml; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        show_raw = params.get("show", [None])[0]
        latest_raw = params.get("latest", [None])[0]

        try:
            request = parse_and_validate(show_raw, latest_raw)
        except ValueError as exc:
            self._send_xml(400, _xml_error(exc))
            return

        host = self.headers.get("Host", "localhost")
        query = {"show": request.show_id}
        if request.latest is not None:
            query["latest"] = request.latest
        self_link = f"//{host}{parsed.path}?{urlencode(query)}"

        try:
            rss_xml = generate_feed(request, self_link)
        except Exception as exc:  # pragma: no cover
            self._send_xml(502, _xml_error(exc))
            return

        self._send_xml(200, rss_xml.encode("utf-8"))


def serve(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), RSSHandler)
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()
