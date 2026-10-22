
import json

import pytest

from app.services.collection_sources import get_sources


def test_no_sources_configured(monkeypatch):
    monkeypatch.delenv("COLLECTION_SOURCES_FILE", raising=False)

    assert get_sources() == []


def test_cheerio_source(tmp_path, monkeypatch):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps([
            {
                "name": "Public Sector Source",
                "url": "https://example.org/records",
                "renderer": "cheerio",
            }
        ]),
        encoding="utf-8",
    )

    monkeypatch.setenv("COLLECTION_SOURCES_FILE", str(path))

    sources = get_sources()

    assert len(sources) == 1
    assert sources[0].name == "Public Sector Source"
    assert sources[0].renderer == "cheerio"


def test_playwright_source(tmp_path, monkeypatch):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps([
            {
                "name": "Dynamic Public Source",
                "url": "https://example.org/dynamic",
                "renderer": "playwright",
            }
        ]),
        encoding="utf-8",
    )

    monkeypatch.setenv("COLLECTION_SOURCES_FILE", str(path))

    sources = get_sources()

    assert len(sources) == 1
    assert sources[0].renderer == "playwright"


def test_default_renderer_is_cheerio(tmp_path, monkeypatch):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps([
            {
                "name": "Default Source",
                "url": "https://example.org/data",
            }
        ]),
        encoding="utf-8",
    )

    monkeypatch.setenv("COLLECTION_SOURCES_FILE", str(path))

    assert get_sources()[0].renderer == "cheerio"


def test_invalid_renderer_rejected(tmp_path, monkeypatch):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps([
            {
                "name": "Invalid Source",
                "url": "https://example.org/data",
                "renderer": "unknown",
            }
        ]),
        encoding="utf-8",
    )

    monkeypatch.setenv("COLLECTION_SOURCES_FILE", str(path))

    with pytest.raises(ValueError, match="Invalid renderer"):
        get_sources()


def test_http_source_rejected(tmp_path, monkeypatch):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps([
            {
                "name": "Insecure Source",
                "url": "http://example.org/data",
            }
        ]),
        encoding="utf-8",
    )

    monkeypatch.setenv("COLLECTION_SOURCES_FILE", str(path))

    with pytest.raises(ValueError, match="Invalid HTTPS source"):
        get_sources()


def test_duplicate_source_names_rejected(tmp_path, monkeypatch):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps([
            {
                "name": "Same Source",
                "url": "https://example.org/one",
            },
            {
                "name": "Same Source",
                "url": "https://example.org/two",
            },
        ]),
        encoding="utf-8",
    )

    monkeypatch.setenv("COLLECTION_SOURCES_FILE", str(path))

    with pytest.raises(ValueError, match="Duplicate source name"):
        get_sources()
