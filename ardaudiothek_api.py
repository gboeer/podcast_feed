from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


GRAPHQL_URL = "https://api.ardaudiothek.de/graphql"


def get_file_length(url: str) -> int:
    """Fetch Content-Length for a remote resource."""
    req = Request(url, method="HEAD")
    try:
        with urlopen(req, timeout=20) as response:
            content_length = response.headers.get("Content-Length")
    except (HTTPError, URLError, ValueError):
        return -1

    try:
        return int(content_length) if content_length is not None else -1
    except ValueError:
        return -1


def get_show_json_graphql(show_id: int, latest: int) -> dict[str, Any]:
    query = (
        "{"
        f"programSet(id:{show_id})"
        "{title,path,synopsis,sharingUrl,image{url,url1X1,},"
        f"items(orderBy:PUBLISH_DATE_DESC,filter:{{isPublished:{{equalTo:true}}}}first:{latest})"
        "{nodes{title,summary,synopsis,sharingUrl,"
        "publicationStartDateAndTime:publishDate,url,episodeNumber,duration,"
        "image{url,url1X1,},isPublished,audios{url,downloadUrl,size,mimeType,}}}}"
        "}"
    )
    body = json.dumps({"query": query}).encode("utf-8")
    req = Request(
        GRAPHQL_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    return payload["data"]["programSet"]
