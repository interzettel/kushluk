"""User-intent source approval is durable, private and never implies full-text rights."""
import json
import os

import pytest

from kushluk.cli import main
from kushluk.config import Settings
from kushluk.opml import parse_opml, write_proposal
from kushluk.source_registry import (
    SourceApprovalError, approve_source, approved_urls, read_registry, revoke_source,
)


def _proposal(tmp_path):
    proposal = tmp_path / "proposal.json"
    feeds = parse_opml(b"""<opml version="2.0"><body>
      <outline text="One" xmlUrl="https://example.org/rss"/>
      <outline text="Two" xmlUrl="https://other.example.net/feed"/>
    </body></opml>""")
    write_proposal(proposal, feeds)
    return proposal


def test_refuses_approval_without_explicit_consent(tmp_path):
    proposal = _proposal(tmp_path)
    registry = tmp_path / "sources.json"
    with pytest.raises(SourceApprovalError, match="acknowledge"):
        approve_source(proposal, 1, acknowledge=False, path=registry)
    assert not registry.exists()


def test_approve_specific_index_then_revoke_without_network(tmp_path, monkeypatch):
    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda *_a, **_k: pytest.fail("network"))
    proposal = _proposal(tmp_path)
    registry = tmp_path / "sources.json"
    first, count, created = approve_source(proposal, 2, acknowledge=True, path=registry)
    assert (count, created) == (1, True)
    assert approved_urls(registry) == ("https://other.example.net/feed",)
    if os.name != "nt":
        assert registry.stat().st_mode & 0o777 == 0o600
    doc = json.loads(registry.read_text())
    assert doc["sources"][0]["mode"] == "reference-only"
    assert doc["sources"][0]["enabled"] is True
    assert len(first) == 20

    second, count, created = approve_source(proposal, 2, acknowledge=True, path=registry)
    assert (second, count, created) == (first, 1, False)
    other, count, created = approve_source(proposal, 1, acknowledge=True, path=registry)
    assert other != first and count == 2 and created is True
    remaining, changed = revoke_source(first, path=registry)
    assert (remaining, changed) == (1, True)
    assert approved_urls(registry) == ("https://example.org/rss",)
    assert not (tmp_path / "sources.json.lock").exists()


def test_registry_only_source_config_has_no_implicit_hackernews(tmp_path, monkeypatch):
    proposal = _proposal(tmp_path)
    registry = tmp_path / "sources.json"
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(registry))
    monkeypatch.delenv("KUSHLUK_RSS_URLS", raising=False)
    # When no registry exists, preserve historical sample source.
    assert Settings.from_env().rss_urls == ("https://hnrss.org/frontpage",)
    approve_source(proposal, 1, acknowledge=True, path=registry)
    assert Settings.from_env().rss_urls == ("https://example.org/rss",)
    monkeypatch.setenv("KUSHLUK_RSS_URLS", "https://explicit.example.com/rss")
    assert Settings.from_env().rss_urls == (
        "https://explicit.example.com/rss", "https://example.org/rss"
    )
    source_id = read_registry(registry)[0]["id"]
    revoke_source(source_id, path=registry)
    monkeypatch.delenv("KUSHLUK_RSS_URLS", raising=False)
    assert Settings.from_env().rss_urls == ()


def test_registry_tamper_fails_closed(tmp_path, monkeypatch):
    path = tmp_path / "sources.json"
    path.write_text('{"version":1,"sources":[{"enabled":true,"url":"file:///secret"}]}')
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(path))
    with pytest.raises(SourceApprovalError):
        Settings.from_env()


def test_approval_rejects_changed_or_activated_proposal(tmp_path):
    proposal = _proposal(tmp_path)
    doc = json.loads(proposal.read_text())
    doc["feeds"][0]["enabled"] = True
    proposal.write_text(json.dumps(doc))
    with pytest.raises(SourceApprovalError, match="proposal"):
        approve_source(proposal, 1, acknowledge=True, path=tmp_path / "sources.json")


@pytest.mark.parametrize("index", [0, -1, 3, 1000])
def test_out_of_range_never_writes_registry(tmp_path, index):
    p = _proposal(tmp_path)
    registry = tmp_path / "sources.json"
    with pytest.raises(SourceApprovalError):
        approve_source(p, index, acknowledge=True, path=registry)
    assert not registry.exists()


def test_lock_is_fail_closed_and_preserves_data(tmp_path):
    p = _proposal(tmp_path)
    registry = tmp_path / "sources.json"
    approve_source(p, 1, acknowledge=True, path=registry)
    data = registry.read_bytes()
    (tmp_path / "sources.json.lock").write_bytes(b"interrupted update")
    with pytest.raises(SourceApprovalError, match="locked"):
        approve_source(p, 2, acknowledge=True, path=registry)
    assert registry.read_bytes() == data


def test_cli_does_not_print_private_feed_urls(tmp_path, monkeypatch, capsys):
    p = _proposal(tmp_path)
    registry = tmp_path / "sources.json"
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(registry))
    assert main(["sources-approve", str(p), "--index", "1"]) == 2
    assert not registry.exists()
    capsys.readouterr()
    assert main([
        "sources-approve", str(p), "--index", "1", "--acknowledge-feed-access",
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "approved"
    assert result["article_copying_permitted"] is False
    assert result["mode"] == "reference-only"
    assert "example.org" not in json.dumps(result)
    identifier = result["id"]
    assert main(["sources-list"]) == 0
    assert json.loads(capsys.readouterr().out)["ids"] == [identifier]
    assert main(["sources-revoke", "--id", identifier]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "revoked"
    assert main(["sources-list"]) == 0
    assert json.loads(capsys.readouterr().out)["approved_count"] == 0
