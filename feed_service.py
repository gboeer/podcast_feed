from __future__ import annotations

from ardaudiothek_api import get_file_length, get_show_json_graphql
from rss_xml import build_rss_xml


MAX_INT_32 = 2_147_483_647


def parse_and_validate(show_raw: str | None, latest_raw: str | None) -> tuple[int, int]:
    if show_raw is None or not show_raw.isdigit():
        raise ValueError('Invalid "show" parameter')

    latest = MAX_INT_32 if latest_raw is None else int(latest_raw) if latest_raw.isdigit() else -1
    if latest < 0:
        raise ValueError('Invalid "latest" parameter')

    return int(show_raw), latest


def generate_feed(show_id: int, latest: int, self_link: str) -> str:
    show = get_show_json_graphql(show_id, latest)
    return build_rss_xml(show, self_link, get_file_length=get_file_length)
