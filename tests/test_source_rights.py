"""Four persisted rights choices; only reference-only may execute today."""
import json
import pytest

from kushluk.cli import main
from kushluk.config import Settings
from kushluk.connectors.rss import RSSConnector
from kushluk.opml import parse_opml, write_proposal
from kushluk.source_registry import (
    SourceApprovalError, approve_source, read_registry, set_source_mode,
)


def _fixture(tmp_path, monkeypatch):
    proposal = tmp_path / "draft.json"
    write_proposal(proposal, parse_opml(
        b'<opml version="2.0"><body><outline xmlUrl="https://example.org/feed" '
        b'text="Example"/></body></opml>'
    ))
    registry = tmp_path / "sources.json"
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(registry))
    monkeypatch.delenv("KUSHLUK_RSS_URLS", raising=False)
    identifier, _, _ = approve_source(proposal, 1, acknowledge=True, path=registry)
    return registry, identifier


def test_four_modes_are_persisted_but_only_reference_is_active(tmp_path, monkeypatch):
    registry, identifier = _fixture(tmp_path, monkeypatch)
    for chosen, expected_enabled in [
        ("ignore", False), ("derivative", False),
        ("private-direct", False), ("reference-only", True),
    ]:
        mode, enabled = set_source_mode(
            identifier, chosen, acknowledge=True, path=registry
        )
        assert (mode, enabled) == (chosen, expected_enabled)
        row = read_registry(registry)[0]
        assert row["mode"] == chosen and row["enabled"] is expected_enabled
        settings = Settings.from_env()
        assert settings.rss_urls == (
            ("https://example.org/feed",) if expected_enabled else ()
        )
        assert settings.reference_only_rss_urls == settings.rss_urls


def test_rights_sensitive_mode_requires_explicit_acknowledgement(tmp_path, monkeypatch):
    registry, identifier = _fixture(tmp_path, monkeypatch)
    before = registry.read_bytes()
    with pytest.raises(SourceApprovalError, match="acknowledgement"):
        set_source_mode(identifier, "private-direct", path=registry)
    assert registry.read_bytes() == before


def test_tampered_activation_fails_closed(tmp_path, monkeypatch):
    registry, identifier = _fixture(tmp_path, monkeypatch)
    payload = json.loads(registry.read_text())
    payload["sources"][0]["mode"] = "private-direct"
    payload["sources"][0]["enabled"] = True
    registry.write_text(json.dumps(payload))
    with pytest.raises(SourceApprovalError, match="cannot be active"):
        Settings.from_env()


def test_cli_mode_is_explicit_and_reports_no_copying(tmp_path, monkeypatch, capsys):
    registry, identifier = _fixture(tmp_path, monkeypatch)
    assert main(["sources-set-mode", "--id", identifier, "--mode", "derivative"]) == 2
    capsys.readouterr()
    assert main([
        "sources-set-mode", "--id", identifier, "--mode", "derivative",
        "--acknowledge-rights-boundary",
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["enabled"] is False
    assert result["body_copying_enabled"] is False
    assert "example.org" not in json.dumps(result)
    assert main(["sources-list"]) == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed["sources"][0]["mode"] == "derivative"
    assert listed["sources"][0]["enabled"] is False


def test_reference_feed_excludes_feed_description_from_archived_story(monkeypatch):
    import kushluk.connectors.rss as rss

    class Stream:
        def __enter__(self):
            return self
        def __exit__(self, *_):
            return False
        def read(self):
            return (
                b'<rss version="2.0"><channel><title>Example News</title>'
                b'<item><title>Public headline</title>'
                b'<description>PRIVATE_FULL_TEXT_NEVER_ARCHIVE</description>'
                b'<link>https://example.org/story</link></item>'
                b'</channel></rss>'
            )

    monkeypatch.setattr(rss, "urlopen", lambda *_a, **_k: Stream())
    candidates = RSSConnector(
        ("https://example.org/feed",),
        reference_only_urls=("https://example.org/feed",),
    ).fetch()
    assert len(candidates) == 1
    assert candidates[0].summary == ""
    assert candidates[0].title == "Public headline"
    from kushluk.editor import select_stories
    stories = select_stories(candidates)
    assert stories[0].deck == "Open the source for the full story."
    assert "PRIVATE_FULL_TEXT_NEVER_ARCHIVE" not in json.dumps(
        [vars(s) if hasattr(s, "__dict__") else s.deck for s in stories]
    )


def test_unapproved_legacy_env_does_not_inherit_registry_reference_mode(tmp_path, monkeypatch):
    registry, identifier = _fixture(tmp_path, monkeypatch)
    set_source_mode(identifier, "ignore", path=registry)
    monkeypatch.setenv("KUSHLUK_RSS_URLS", "https://other.example.net/feed")
    settings = Settings.from_env()
    assert settings.rss_urls == ("https://other.example.net/feed",)
    assert settings.reference_only_rss_urls == ()
