"""External story links must never expose tokenized feeds or create unsafe hrefs."""
from datetime import date
import json
from zipfile import ZipFile

import pytest

from kushluk.connectors import rss
from kushluk.epub import export_archived_epub
from kushluk.feed_network import public_article_link
from kushluk.models import Story, PracticalItem
from kushluk.publication import build_publication


@pytest.mark.parametrize("url", [
    "javascript:alert(1)",
    "file:///private",
    "https://127.0.0.1/private",
    "http://10.0.0.1/",
    "https://metadata.google.internal/latest",
    "https://u:pwd@example.org/article",
    "https://example.org/article?access_token=mysecret",
    "https://example.org/story?api_key=secret",
    "https://example.org/story?subscriptionid=abc&token=secret",
    "https://example.org/story?session_id=private",
    "/relative/path",
])
def test_bad_or_credentialed_article_urls_never_published(url):
    assert public_article_link(url) is None


def test_valid_article_links_preserve_story_id_and_remove_fragment():
    assert (
        public_article_link("https://example.org/read?id=123&lang=de#private-note")
        == "https://example.org/read?id=123&lang=de"
    )


def test_rss_denies_unsafe_item_href_and_keeps_headline(monkeypatch):
    def fake(_url):
        return (
            b'<rss><channel><title>Publisher</title>'
            b'<item><title>Personal-safe headline</title>'
            b'<link>javascript:alert(1)</link></item>'
            b'<item><title>Secret link story</title>'
            b'<link>https://example.org/p?access_token=SECRET</link></item>'
            b'</channel></rss>'
        )
    monkeypatch.setattr(rss, "fetch_public_xml", fake)
    rows = rss.RSSConnector(("https://myfeed.example.org/feed?token=FEEDSECRET",)).fetch()
    assert len(rows) == 2
    assert all(x.url is None for x in rows)
    assert all(x.summary == "" for x in rows)
    assert "FEEDSECRET" not in repr(rows)
    assert "SECRET" not in repr(rows)


def test_old_archived_links_are_revalidated_for_epub(tmp_path):
    root = tmp_path / "archive"
    folder = root / "20261017-001"
    folder.mkdir(parents=True)
    edition = build_publication(
        target_date=date(2026, 10, 17),
        timezone="Europe/Berlin",
        location_name="Synthetic",
        practical=[PracticalItem("Test", "No personal data")],
        stories=[
            Story("s1", "Synthetic story", "Synthetic short description", "Example",
                  source_url="https://news.example.org/a?session=SECRET"),
        ],
    )
    (folder / "metadata.json").write_text(json.dumps(edition.to_dict()))
    path = tmp_path / "test.epub"
    export_archived_epub(root, date(2026, 10, 17), path)
    with ZipFile(path) as z:
        content = b"".join(z.read(n) for n in z.namelist())
    assert b"SECRET" not in content
    assert b"Source: Example" in content
