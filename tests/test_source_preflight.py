"""Source preflight never creates an edition or contacts providers by default."""
import json
import os

import pytest

from kushluk.cli import main
from kushluk.opml import parse_opml, write_proposal
from kushluk.source_preflight import (
    SourcePreflightError, check_sources, save_private_preflight,
)
from kushluk.source_registry import approve_source, set_source_mode


def _registry(tmp_path):
    proposal = tmp_path / "proposal.json"
    write_proposal(proposal, parse_opml(
        b'<opml version="2.0"><body>'
        b'<outline text="One" xmlUrl="https://one.example.org/rss?key=SECRET_TOKEN"/>'
        b'<outline text="Two" xmlUrl="https://two.example.org/rss"/>'
        b'<outline text="Three" xmlUrl="https://three.example.org/rss"/>'
        b'</body></opml>'
    ))
    path = tmp_path / "approved.json"
    ids = []
    for index in (1, 2, 3):
        identifier, _, _ = approve_source(
            proposal, index, acknowledge=True, path=path
        )
        ids.append(identifier)
    set_source_mode(ids[2], "private-direct", acknowledge=True, path=path)
    return path, ids


def test_preflight_offline_default_is_strictly_no_network(tmp_path, monkeypatch):
    registry, ids = _registry(tmp_path)
    import kushluk.source_preflight as module
    monkeypatch.setattr(
        module.RSSConnector, "fetch", lambda _self: pytest.fail("network not approved"),
    )
    before = registry.read_bytes()
    report = check_sources(path=registry)
    assert report["status"] == "offline_inventory"
    assert report["network_requested"] is False
    assert report["checked_sources"] == 0
    assert report["active_sources"] == 2
    assert report["sources_modified"] is False
    assert report["archive_modified"] is False
    assert report["editions_created"] == 0
    assert report["rights_verified"] is False
    assert {item["id"] for item in report["sources"]} == set(ids)
    assert registry.read_bytes() == before
    assert "SECRET_TOKEN" not in json.dumps(report)


def test_preflight_network_checks_only_explicit_approved_feeds(tmp_path, monkeypatch):
    registry, ids = _registry(tmp_path)
    seen = []

    def fake_fetch(self):
        seen.extend(self.urls)
        if "two.example.org" in self.urls[0]:
            self.failed_feeds = [
                {"feed_number": 1, "reason": "unsafe_or_unavailable"}
            ]
            return []
        return [object(), object()]

    monkeypatch.setattr(
        "kushluk.source_preflight.RSSConnector.fetch", fake_fetch,
    )
    report = check_sources(path=registry, network=True)
    assert report["checked_sources"] == 2
    assert report["reachable_sources"] == 1
    assert report["failed_sources"] == 1
    assert report["status"] == "partial_or_unavailable"
    assert len(seen) == 2
    assert "three.example.org" not in str(seen)
    assert "SECRET_TOKEN" not in str(report)
    assert set(entry["id"] for entry in report["sources"]) == set(ids)


def test_preflight_respects_limit_and_never_contacts_disabled(tmp_path, monkeypatch):
    registry, ids = _registry(tmp_path)
    seen = []
    def fake_fetch(self):
        seen.extend(self.urls)
        return [object()]
    monkeypatch.setattr("kushluk.source_preflight.RSSConnector.fetch", fake_fetch)
    report = check_sources(path=registry, network=True, limit=1)
    assert report["checked_sources"] == 1
    assert report["remaining_active_sources"] == 1
    assert report["status"] == "partial_or_unavailable"
    assert len(seen) == 1
    assert report["sources"][-1]["status"] == "not_checked"


@pytest.mark.parametrize("limit", [0, -1, 11, True, 1.0])
def test_invalid_limit_fails_before_contact(tmp_path, limit):
    with pytest.raises(SourcePreflightError):
        check_sources(path=tmp_path / "none.json", network=True, limit=limit)


def test_cli_dry_run_and_private_report_no_overwrite(tmp_path, monkeypatch, capsys):
    registry, ids = _registry(tmp_path)
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(registry))
    monkeypatch.setattr(
        "kushluk.source_preflight.RSSConnector.fetch",
        lambda _: pytest.fail("must not contact feeds"),
    )
    report_path = tmp_path / "source-report.json"
    args = ["sources-preflight", "--output", str(report_path)]
    assert main(args) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["network_requested"] is False
    assert result["active_sources"] == 2
    assert len(result["sources"]) == 3
    assert report_path.is_file()
    if os.name != "nt":
        assert report_path.stat().st_mode & 0o777 == 0o600
    before = report_path.read_bytes()
    assert main(args) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "rejected"
    assert report_path.read_bytes() == before


def test_preflight_error_redacts_unexpected_failure(tmp_path, monkeypatch):
    registry, _ = _registry(tmp_path)
    monkeypatch.setattr(
        "kushluk.source_preflight.RSSConnector.fetch",
        lambda _self: (_ for _ in ()).throw(
            RuntimeError("A private querystring was visible to remote provider")
        )
    )
    report = check_sources(path=registry, network=True, limit=2)
    assert report["failed_sources"] == 2
    assert all(
        row["status"] == "unexpected_failure" for row in report["sources"]
        if row["checked"]
    )
    assert "querystring" not in str(report)


def test_export_private_json_does_not_touch_registry(tmp_path):
    registry, _ = _registry(tmp_path)
    before = registry.read_bytes()
    report = check_sources(path=registry)
    path = tmp_path / "audit.json"
    save_private_preflight(report, path)
    assert json.loads(path.read_text())["network_requested"] is False
    assert registry.read_bytes() == before
