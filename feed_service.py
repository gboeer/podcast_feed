from __future__ import annotations

import re
from dataclasses import dataclass

from ardaudiothek_api import get_file_length, get_show_json_graphql
from rss_xml import build_rss_xml

SHOW_URN_PREFIX = "urn:ard:show:"
SHOW_TOKEN_PATTERN = re.compile(r"^[a-z0-9]+$")


@dataclass(frozen=True)
class FeedRequest:
    show_id: str
    latest: int | None = None


def _parse_show_id(raw: str | None) -> str:
    if raw is None:
        raise ValueError('Invalid "show" parameter')

    show_id_raw = raw.strip().lower()
    if not show_id_raw:
        raise ValueError('Invalid "show" parameter')

    show_token = (
        show_id_raw[len(SHOW_URN_PREFIX) :]
        if show_id_raw.startswith(SHOW_URN_PREFIX)
        else show_id_raw
    )
    if not SHOW_TOKEN_PATTERN.fullmatch(show_token) or show_token.isdigit():
        raise ValueError(
            'Invalid "show" parameter: pass the ARD show token (for example "8e6d4d6fa453e7f7")'
        )

    return f"{SHOW_URN_PREFIX}{show_token}"


def _parse_positive_int(name: str, raw: str | None, *, required: bool) -> int | None:
    if raw is None or raw == "":
        if required:
            raise ValueError(f'Invalid "{name}" parameter')
        return None

    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f'Invalid "{name}" parameter') from exc

    if value <= 0:
        raise ValueError(f'Invalid "{name}" parameter')
    return value


def parse_and_validate(show_raw: str | None, latest_raw: str | None) -> FeedRequest:
    return FeedRequest(
        show_id=_parse_show_id(show_raw),
        latest=_parse_positive_int("latest", latest_raw, required=False),
    )


def generate_feed(request: FeedRequest, self_link: str) -> str:
    show = get_show_json_graphql(request.show_id, request.latest)
    return build_rss_xml(show, self_link, get_file_length=get_file_length)
