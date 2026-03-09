#!/usr/bin/env python3
"""Generate a simple GitHub Pages landing page for available podcast feeds."""

from __future__ import annotations

import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).parent
PODCASTS_FILE = ROOT / "podcasts.json"
PUBLIC_DIR = ROOT / "public"
INDEX_FILE = PUBLIC_DIR / "index.html"


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
        search_text = html.escape(f"{name} {feed_url}".lower(), quote=True)
        items.append(
            (
                f'<li data-search="{search_text}">'
                f"<strong>{escaped_name}</strong><br>"
                f'<a href="{escaped_url}">{escaped_url}</a>'
                "</li>"
            )
        )

    items_markup = "\n".join(items)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Podcast Feeds</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f8f8f5;
      --text: #1d1d1b;
      --muted: #555;
      --card: #fff;
      --line: #ddd;
      --accent: #0d5f9a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Helvetica, Arial, sans-serif;
      color: var(--text);
      background: linear-gradient(180deg, #ecebe6 0%, var(--bg) 30%);
      min-height: 100vh;
    }}
    main {{
      max-width: 780px;
      margin: 0 auto;
      padding: 40px 20px 60px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 2rem;
    }}
    p {{
      margin: 0 0 16px;
      color: var(--muted);
      line-height: 1.5;
    }}
    .controls {{
      display: grid;
      gap: 8px;
    }}
    input[type="search"] {{
      width: 100%;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      font-size: 1rem;
      background: #fff;
      color: var(--text);
    }}
    .stats {{
      color: var(--muted);
      font-size: 0.95rem;
    }}
    ul {{
      list-style: none;
      padding: 0;
      margin: 24px 0;
    }}
    li {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 14px 16px;
      margin-bottom: 12px;
    }}
    a {{
      color: var(--accent);
      overflow-wrap: anywhere;
      text-decoration: none;
    }}
    a:hover {{ text-decoration: underline; }}
    footer {{
      margin-top: 26px;
      color: var(--muted);
      font-size: 0.9rem;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Podcast RSS Feeds</h1>
    <p>Welcome. This page lists all currently published podcast feed URLs for this repository.</p>
    <div class="controls">
      <label for="feed-search">Search feeds</label>
      <input id="feed-search" type="search" placeholder="Type podcast name or URL" autocomplete="off">
      <div id="feed-stats" class="stats"></div>
    </div>
    <ul>
{items_markup}
    </ul>
    <footer>Generated at {generated_at}</footer>
  </main>
  <script>
    (function () {{
      const input = document.getElementById("feed-search");
      const stats = document.getElementById("feed-stats");
      const items = Array.from(document.querySelectorAll("li[data-search]"));
      const total = items.length;

      function update() {{
        const q = input.value.trim().toLowerCase();
        let visible = 0;
        for (const item of items) {{
          const haystack = item.dataset.search || "";
          const match = q === "" || haystack.includes(q);
          item.style.display = match ? "" : "none";
          if (match) visible += 1;
        }}
        stats.textContent = q ? `${{visible}} of ${{total}} feeds` : `${{total}} feeds`;
      }}

      input.addEventListener("input", update);
      update();
    }})();
  </script>
</body>
</html>
"""


def main() -> int:
    podcasts = json.loads(PODCASTS_FILE.read_text(encoding="utf-8"))
    feed_base_url = _feed_base_url()

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(
        _build_index_html(podcasts, feed_base_url),
        encoding="utf-8",
    )
    print(f"Saved -> {INDEX_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
