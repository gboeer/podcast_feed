# RSS Feeds für ARDSounds / ARD Audiothek

[English README](README.en.md)

Dieses Projekt erzeugt RSS-Feeds für Podcasts von [ARDSounds](https://www.ardsounds.de) (ehemals ARD Audiothek).  

## Öffentlich verfügbare Feeds (GitHub Pages)

Die Feeds werden über GitHub Pages veröffentlicht.

- Landing Page mit Feed-Suche: https://gboeer.github.io/podcast_feed/
- Feed-URLs: `https://gboeer.github.io/podcast_feed/feeds/<podcast_slug>.xml`

Für ein User/Org-Pages-Repo (`<owner>.github.io`) ist das Schema:
- Landing Page: `https://<owner>.github.io/`
- Feed-URLs: `https://<owner>.github.io/feeds/<podcast_slug>.xml`

Hier ist eine Liste mit allen verfügbaren Podcasts: https://gist.github.com/gboeer/242909e4959fd0b1b47c1a9e5529fea1

## Veröffentlichung per GitHub Actions

Der Workflow [.github/workflows/fetch-feeds.yml](.github/workflows/fetch-feeds.yml):
- lädt die konfigurierten Podcasts aus `podcasts.json`
- erzeugt XML-Dateien in `feeds/`
- erzeugt eine Landing Page (`index.html`) in `public/`
- deployed alles auf den Branch `gh-pages`

Einmalige GitHub-Einstellung:
- `Settings -> Pages -> Build and deployment -> Source`
- `Deploy from a branch`
- Branch: `gh-pages`, Folder: `/ (root)`

## Selbst hosten

### 1. Einzelnen Feed erzeugen (CLI)

Jeder Sendung wird eine eindeutige ID zugewiesen, die über die ARDSounds-URL abgerufen werden kann: Beispielsweise lautet die ID für https://www.ardsounds.de/sendung/kalk-und-welk/urn:ard:show:8e6d4d6fa453e7f7/  --> 8e6d4d6fa453e7f7.

Rufe die neuesten 10 Episoden von „Kalk und Welk” ab.
```bash
python3 ardaudiothek_rss.py --show 8e6d4d6fa453e7f7 --latest 10
```

Optional mit explizitem Atom-Self-Link:

```bash
python3 ardaudiothek_rss.py --show 8e6d4d6fa453e7f7 --latest 10 \
  --self-link "https://example.com/feeds/kalk___welk.xml"
```

### 2. Lokalen HTTP-Service starten

```bash
python3 ardaudiothek_rss.py --serve --port 8000
```

Beispielaufruf:

```text
http://localhost:8000/?show=8e6d4d6fa453e7f7&latest=10
```

### 3. Mehrere Feeds auf einmal erzeugen

Die Datei `podcasts.json` enthält die Liste der zu erzeugenden Feeds:

```bash
python3 fetch_feeds.py
```

Mit eigener Basis-URL für atom:self:

```bash
FEED_BASE_URL="https://example.com/feeds" python3 fetch_feeds.py
```

## Danksagung

Dieses Projekt begann als Python-Neuimplementierung des ursprünglichen PHP-Projekts:
 
https://github.com/matztam/ARD-Audiothek-RSS
