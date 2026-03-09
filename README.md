# podcast_feed

Python rebuild of the ARD Audiothek RSS PHP endpoint (Original: https://github.com/matztam/ARD-Audiothek-RSS).

## Usage

Generate a feed once (prints RSS XML to stdout):

```bash
python3 ardaudiothek_rss.py --show 8e6d4d6fa453e7f7 --latest 10
```

Run as a local HTTP service:

```bash
python3 ardaudiothek_rss.py --serve --port 8000
# http://localhost:8000/?show=8e6d4d6fa453e7f7&latest=10
```

## Publishing with GitHub Pages

The workflow at `.github/workflows/fetch-feeds.yml` can publish generated feeds to a `gh-pages` branch.

One-time GitHub setting:
- `Settings -> Pages -> Build and deployment -> Source`: select `Deploy from a branch`
- Branch: `gh-pages`, folder: `/ (root)`

After each run, feeds are available at:
- `https://<owner>.github.io/<repo>/feeds/<podcast_slug>.xml`
- user/organization pages repo (`<owner>.github.io`): `https://<owner>.github.io/feeds/<podcast_slug>.xml`

Landing page:
- `https://<owner>.github.io/<repo>/`
- lists all configured podcast feed URLs from `podcasts.json`

## Structure

- `ardaudiothek_rss.py`: CLI entrypoint and server startup switch.
- `rss_server.py`: HTTP request handling.
- `feed_service.py`: input validation and feed orchestration.
- `ardaudiothek_api.py`: ARD API calls and audio metadata lookup.
- `rss_xml.py`: RSS XML serialization.
