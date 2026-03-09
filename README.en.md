# RSS Feeds for ARDSounds / ARD Audiothek

[Deutsches README](README.md)

This project generates RSS feeds for podcasts from ARD Audiothek.  
It is a Python reimplementation of the original PHP project:  
https://github.com/matztam/ARD-Audiothek-RSS

## Public feeds (GitHub Pages)

Feeds are published via GitHub Pages.

- Landing page with feed search: `https://gboeer.github.io/podcast_feed/`
- Feed URLs: `https://gboeer.github.io/podcast_feed/feeds/<podcast_slug>.xml`

For a user/org pages repo (`<owner>.github.io`), the URL pattern is:
- Landing page: `https://<owner>.github.io/`
- Feed URLs: `https://<owner>.github.io/feeds/<podcast_slug>.xml`

## Publishing via GitHub Actions

The workflow [.github/workflows/fetch-feeds.yml](.github/workflows/fetch-feeds.yml):
- loads configured podcasts from `podcasts.json`
- generates XML files in `feeds/`
- builds a landing page (`index.html`) in `public/`
- deploys everything to the `gh-pages` branch

One-time GitHub setting:
- `Settings -> Pages -> Build and deployment -> Source`
- `Deploy from a branch`
- Branch: `gh-pages`, Folder: `/ (root)`

## Self-hosting

### 1. Generate a single feed (CLI)

```bash
python3 ardaudiothek_rss.py --show 8e6d4d6fa453e7f7 --latest 10
```

Optional with explicit atom:self link:

```bash
python3 ardaudiothek_rss.py --show 8e6d4d6fa453e7f7 --latest 10 \
  --self-link "https://example.com/feeds/kalk___welk.xml"
```

### 2. Run local HTTP service

```bash
python3 ardaudiothek_rss.py --serve --port 8000
```

Example request:

```text
http://localhost:8000/?show=8e6d4d6fa453e7f7&latest=10
```

### 3. Generate multiple feeds in batch

`podcasts.json` defines which feeds are generated:

```bash
python3 fetch_feeds.py
```

With custom atom:self base URL:

```bash
FEED_BASE_URL="https://example.com/feeds" python3 fetch_feeds.py
```

## Project structure

- `ardaudiothek_rss.py`: CLI entrypoint and optional HTTP server
- `fetch_feeds.py`: batch generation for all feeds in `podcasts.json`
- `build_pages_index.py`: creates landing page for GitHub Pages
- `rss_server.py`: HTTP request handling
- `feed_service.py`: validation and feed orchestration
- `ardaudiothek_api.py`: API requests and audio metadata
- `rss_xml.py`: RSS serialization
