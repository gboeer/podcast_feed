"""Paths and naming shared by the batch scripts, so feed filenames and URLs always match."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).parent
PODCASTS_FILE = ROOT / "podcasts.json"
FEEDS_DIR = ROOT / "feeds"


SHOW_URN_PREFIX = "urn:ard:show:"


def feed_filename(show_id: str) -> str:
    """Feed filename for a show: its ARD show token, which never changes (unlike the title)."""
    token = show_id.strip().lower()
    if token.startswith(SHOW_URN_PREFIX):
        token = token[len(SHOW_URN_PREFIX) :]
    return f"{token}.xml"


def feed_base_url() -> str:
    """Base URL used for atom:self links and landing-page links."""
    return os.getenv("FEED_BASE_URL", "http://localhost:8000/feeds").rstrip("/")
