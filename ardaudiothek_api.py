from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


GRAPHQL_URL = "https://api.ardaudiothek.de/graphql"
API_TIMEOUT_SECONDS = 30
HEAD_TIMEOUT_SECONDS = 20

PROGRAMSET_QUERY = """
query ProgramSet($id: Int!, $first: Int) {
  programSet(id: $id) {
    title
    path
    synopsis
    sharingUrl
    image { url url1X1 }
    items(
      orderBy: PUBLISH_DATE_DESC
      filter: { isPublished: { equalTo: true } }
      first: $first
    ) {
      nodes {
        title
        summary
        synopsis
        sharingUrl
        publicationStartDateAndTime: publishDate
        url
        episodeNumber
        duration
        image { url url1X1 }
        isPublished
        audios { url downloadUrl size mimeType }
      }
    }
  }
}
"""


def get_file_length(url: str) -> int | None:
    """Fetch Content-Length for a remote resource."""
    req = Request(url, method="HEAD")
    try:
        with urlopen(req, timeout=HEAD_TIMEOUT_SECONDS) as response:
            content_length = response.headers.get("Content-Length")
    except (HTTPError, URLError, ValueError):
        return None

    try:
        return int(content_length) if content_length is not None else None
    except ValueError:
        return None


def get_show_json_graphql(show_id: int, latest: int | None) -> dict[str, Any]:
    body = json.dumps(
        {"query": PROGRAMSET_QUERY, "variables": {"id": show_id, "first": latest}}
    ).encode("utf-8")
    req = Request(
        GRAPHQL_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(req, timeout=API_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if payload.get("errors"):
        raise ValueError(f"GraphQL error: {payload['errors']}")
    return payload["data"]["programSet"]
