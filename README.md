# podcast_feed

Python rebuild of the ARD Audiothek RSS PHP endpoint (Original: https://github.com/matztam/ARD-Audiothek-RSS).

## Usage

Generate a feed once (prints RSS XML to stdout):

```bash
python3 ardaudiothek_rss.py --show 10777871 --latest 10
```

Run as a local HTTP service:

```bash
python3 ardaudiothek_rss.py --serve --port 8000
# http://localhost:8000/?show=10777871&latest=10
```

## Structure

- `ardaudiothek_rss.py`: CLI entrypoint and server startup switch.
- `rss_server.py`: HTTP request handling.
- `feed_service.py`: input validation and feed orchestration.
- `ardaudiothek_api.py`: ARD API calls and audio metadata lookup.
- `rss_xml.py`: RSS XML serialization.
