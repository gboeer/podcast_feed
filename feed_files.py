"""Paths and naming shared by the batch scripts, so feed filenames and URLs always match."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).parent
PODCASTS_FILE = ROOT / "podcasts.json"
FEEDS_DIR = ROOT / "feeds"


def feed_slug(name: str) -> str:
    """Convert a podcast name to a safe filename stem."""
    return "".join(c if c.isalnum() else "_" for c in name).strip("_").lower()


def feed_base_url() -> str:
    """Base URL used for atom:self links and landing-page links."""
    return os.getenv("FEED_BASE_URL", "http://localhost:8000/feeds").rstrip("/")
