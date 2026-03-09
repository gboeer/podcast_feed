from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from typing import Any, Callable
from xml.etree import ElementTree as ET

ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
ET.register_namespace("media", "http://search.yahoo.com/mrss/")
ET.register_namespace("itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")


def _format_rss_pubdate(iso_dt: str) -> str:
    dt = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return format_datetime(dt)


def _replace_width(url_template: str, width: str = "448") -> str:
    return url_template.replace("{width}", width)


def _episode_description(node: dict[str, Any]) -> str:
    return node.get("summary") or node.get("synopsis") or ""


def build_rss_xml(
    show: dict[str, Any],
    self_link: str,
    get_file_length: Callable[[str], int | None],
) -> str:
    rss = ET.Element(
        "rss",
        {
            "version": "2.0",
        },
    )
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = show.get("title", "")
    ET.SubElement(channel, "link").text = show.get("sharingUrl", "")

    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = _replace_width(
        show.get("image", {}).get("url1X1", "")
    )
    ET.SubElement(image, "title").text = show.get("title", "")
    ET.SubElement(
        image, "link"
    ).text = f"https://www.ardaudiothek.de{show.get('path', '')}"

    ET.SubElement(channel, "description").text = show.get("synopsis", "")
    ET.SubElement(
        channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}language"
    ).text = "de-DE"
    ET.SubElement(
        channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}category", {"text": "News"}
    )
    ET.SubElement(
        channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit"
    ).text = "false"
    ET.SubElement(
        channel,
        "{http://www.w3.org/2005/Atom}link",
        {"href": self_link, "rel": "self", "type": "application/rss+xml"},
    )

    for node in show.get("items", {}).get("nodes", []):
        item = ET.SubElement(channel, "item")
        audios = node.get("audios") or []
        primary_audio = audios[0] if audios else {}

        audio_url = primary_audio.get("url") or ""
        download_url = primary_audio.get("downloadUrl") or ""
        mime_type = primary_audio.get("mimeType") or "audio/mpeg"
        duration = int(node.get("duration") or 0)
        length = get_file_length(audio_url) if audio_url else None

        ET.SubElement(item, "title").text = node.get("title", "")
        ET.SubElement(item, "description").text = _episode_description(node)
        ET.SubElement(item, "guid").text = node.get("sharingUrl", "")
        ET.SubElement(item, "link").text = node.get("sharingUrl", "")
        ET.SubElement(
            item,
            "enclosure",
            {"url": audio_url, "length": str(length or 0), "type": mime_type},
        )
        ET.SubElement(
            item,
            "{http://search.yahoo.com/mrss/}content",
            {
                "url": download_url,
                "medium": "audio",
                "duration": str(duration),
                "type": mime_type,
            },
        )

        publish_date = node.get("publicationStartDateAndTime")
        if publish_date:
            ET.SubElement(item, "pubDate").text = _format_rss_pubdate(publish_date)
        ET.SubElement(
            item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}duration"
        ).text = str(duration)

        item_image_url = _replace_width(node.get("image", {}).get("url1X1", ""))
        ET.SubElement(
            item,
            "{http://www.itunes.com/dtds/podcast-1.0.dtd}image",
            {"href": item_image_url},
        )

    xml = ET.tostring(rss, encoding="utf-8", xml_declaration=False)
    return xml.decode("utf-8")
