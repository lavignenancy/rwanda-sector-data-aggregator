import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class CollectionSource:
    name: str
    url: str
    renderer: str = "cheerio"


def get_sources() -> list[CollectionSource]:
    config_path = os.getenv("COLLECTION_SOURCES_FILE")

    if not config_path:
        return []

    data = json.loads(Path(config_path).read_text(encoding="utf-8"))

    if not isinstance(data, list):
        raise ValueError("Collection sources must be a list")

    sources = []
    names = set()

    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Invalid collection source")

        name = item.get("name")
        url = item.get("url")
        renderer = item.get("renderer", "cheerio")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Source name is required")

        if not isinstance(url, str):
            raise ValueError("Source URL is required")

        parsed = urlparse(url)

        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.port
            or parsed.fragment
        ):
            raise ValueError(f"Invalid HTTPS source: {name}")

        if renderer not in ("cheerio", "playwright"):
            raise ValueError(f"Invalid renderer: {renderer}")

        if name in names:
            raise ValueError(f"Duplicate source name: {name}")

        names.add(name)

        sources.append(
            CollectionSource(
                name=name,
                url=url,
                renderer=renderer,
            )
        )

    return sources
