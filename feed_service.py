from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from ardaudiothek_api import get_file_length, get_show_json_graphql
from rss_xml import build_rss_xml


@dataclass(frozen=True)
class FeedRequest:
    show_id: int
    latest: int | None = None


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
    show_id = cast(int, _parse_positive_int("show", show_raw, required=True))
    return FeedRequest(
        show_id=show_id,
        latest=_parse_positive_int("latest", latest_raw, required=False),
    )


def generate_feed(request: FeedRequest, self_link: str) -> str:
    show = get_show_json_graphql(request.show_id, request.latest)
    return build_rss_xml(show, self_link, get_file_length=get_file_length)
