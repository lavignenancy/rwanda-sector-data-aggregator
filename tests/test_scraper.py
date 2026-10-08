from app.scraper import make_hash, parse_html, parse_json


def test_make_hash_is_deterministic():
    a = make_hash("source", "item", "Title", "Description")
    b = make_hash("source", "item", "Title", "Description")
    assert a == b
    assert len(a) == 64


def test_parse_html():
    html = '''
    <html><body>
      <article>
        <h2>Health update</h2>
        <p>New information.</p>
        <a href="/health/1">Read</a>
      </article>
    </body></html>
    '''
    source = {
        "url": "https://example.org/news",
        "selectors": {
            "items": "article",
            "title": "h2",
            "description": "p",
            "link": "a"
        }
    }
    records = parse_html(html, source)
    assert len(records) == 1
    assert records[0]["title"] == "Health update"
    assert records[0]["item_url"] == "https://example.org/health/1"


def test_parse_json():
    data = {
        "results": [
            {
                "title": "Agriculture update",
                "description": "New data",
                "url": "https://example.org/a/1",
                "published": "2026-10-05"
            }
        ]
    }
    source = {
        "json_items_path": "results",
        "json_fields": {
            "title": "title",
            "description": "description",
            "url": "url",
            "published_at": "published"
        }
    }
    records = parse_json(data, source)
    assert records[0]["title"] == "Agriculture update"
