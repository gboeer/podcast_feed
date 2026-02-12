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
