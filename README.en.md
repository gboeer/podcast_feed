# RSS Feeds for ARDSounds / ARD Audiothek

[Deutsches README](README.md)

This project generates RSS feeds for podcasts from [ARDSounds](https://www.ardsounds.de) (former ARD Audiothek).  

## Public feeds (GitHub Pages)

Feeds are published via GitHub Pages.

- Landing page with feed search: https://gboeer.github.io/podcast_feed/
- Feed URLs: `https://gboeer.github.io/podcast_feed/feeds/<podcast_slug>.xml`

For a user/org pages repo (`<owner>.github.io`), the URL pattern is:
- Landing page: `https://<owner>.github.io/`
- Feed URLs: `https://<owner>.github.io/feeds/<podcast_slug>.xml`

Here is a list with all available Podcasts: https://gist.github.com/gboeer/242909e4959fd0b1b47c1a9e5529fea1

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

Each show is assigned a unique ID, which can be fetched from the ARDSounds URL: e.g. for https://www.ardsounds.de/sendung/kalk-und-welk/urn:ard:show:8e6d4d6fa453e7f7/ the ID is 8e6d4d6fa453e7f7.

Fetch the newest 10 Episodes of "Kalk und Welk".
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

## Appreciation

This projected started as a Python reimplementation of the original PHP project: 

https://github.com/matztam/ARD-Audiothek-RSS
