"""One unreachable feed must not erase the other reader-approved sources."""
from datetime import date
import json

import pytest

from kushluk import pipeline
from kushluk.config import Settings
from kushluk.connectors import rss
from kushluk.feed_network import FeedNetworkError
from kushluk.models import PracticalItem


def _good_feed() -> bytes:
    return (
        b'<rss version="2.0"><channel><title>Source One</title>'
        b'<item><title>Public original headline</title>'
        b'<description>NO_COPY_RIGHTS_RAW_ARTICLE</description>'
        b'<link>https://example.net/original</link></item></channel></rss>'
    )


def test_one_bad_feed_does_not_block_valid_feed(monkeypatch):
    tokenized = "https://private.example.org/rss?token=KEEP_PRIVATE"
    calls = []

    def fetch(url):
        calls.append(url)
        if "private.example.org" in url:
            raise FeedNetworkError("Do not show provider URL, even in debug logs")
        return _good_feed()

    monkeypatch.setattr(rss, "fetch_public_xml", fetch)
    collector = rss.RSSConnector((tokenized, "https://example.org/rss"))
    candidates = collector.fetch()
    assert len(candidates) == 1
    assert candidates[0].title == "Public original headline"
    assert candidates[0].summary == ""
    assert collector.failed_feeds == [
        {"feed_number": 1, "reason": "unsafe_or_unavailable"}
    ]
    assert "KEEP_PRIVATE" not in repr(collector.failed_feeds)
    assert calls == [tokenized, "https://example.org/rss"]

    monkeypatch.setattr(rss, "fetch_public_xml", lambda _url: _good_feed())
    assert len(collector.fetch()) == 2
    assert collector.failed_feeds == []  # State resets on each run.


def test_invalid_xml_isolated_with_redacted_reason(monkeypatch):
    def fetch(url):
        return b"<xml><not-a-valid-feed" if "bad" in url else _good_feed()

    monkeypatch.setattr(rss, "fetch_public_xml", fetch)
    r = rss.RSSConnector(("https://bad.example.org/rss", "https://good.example.org/rss"))
    assert len(r.fetch()) == 1
    assert r.failed_feeds == [{"feed_number": 1, "reason": "invalid_feed_xml"}]


def test_degraded_pipeline_archive_contains_only_healthy_source(tmp_path, monkeypatch):
    monkeypatch.setattr(
        pipeline.OpenMeteoWeatherConnector,
        "fetch",
        lambda self: [PracticalItem("Temperature", "15 C", "Synthetic weather")],
    )
    monkeypatch.setattr(
        pipeline.CalendarFixtureConnector,
        "fetch",
        lambda self: [PracticalItem("Calendar", "Clear", "Synthetic")],
    )

    def fetch(url):
        if "bad.example" in url:
            raise FeedNetworkError("SECRET_PRIVATE_TOKEN=123")
        return _good_feed()

    monkeypatch.setattr(rss, "fetch_public_xml", fetch)
    cfg = Settings(
        archive_dir=tmp_path / "archive",
        output_dir=tmp_path / "output",
        rss_urls=("https://bad.example/rss?token=secret", "https://good.example/rss"),
    )
    result = pipeline.run_pipeline(
        cfg, target_date=date(2026, 10, 17), make_pdf=False
    )
    assert len(result.publication.stories) == 1
    assert result.publication.stories[0].deck == "Open the source for the full story."
    assert any(item.code == "rss_feed_unavailable" for item in result.failures)
    warnings = " ".join(result.warnings)
    assert "SECRET_PRIVATE" not in warnings
    assert "token=secret" not in warnings
    metadata = (result.archive_dir / "metadata.json").read_text()
    assert "NO_COPY_RIGHTS_RAW_ARTICLE" not in metadata
    assert "token=secret" not in metadata
    stored = json.loads(metadata)
    assert stored["stories"][0]["source_url"] == "https://example.net/original"


def test_unexpected_programmer_error_is_not_hidden(monkeypatch):
    monkeypatch.setattr(
        rss, "fetch_public_xml", lambda _url: (_ for _ in ()).throw(AssertionError("bad code"))
    )
    with pytest.raises(AssertionError, match="bad code"):
        rss.RSSConnector(("https://example.org/rss",)).fetch()
