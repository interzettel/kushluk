"""OPML intake is offline, bounded and never silently activates a source."""
import json
import os

import pytest

from kushluk.cli import main
from kushluk.opml import (
    OPMLImportError,
    parse_opml,
    proposal_document,
    read_proposal,
    render_opml,
    write_proposal,
)


def sample_opml() -> bytes:
    return b"""<?xml version="1.0"?>
<opml version="2.0">
  <head><title>Reader subscriptions</title></head>
  <body>
    <outline text="Tech">
      <outline type="rss" text="Example &amp; Co" xmlUrl="https://EXAMPLE.com:443/feed"/>
      <outline type="rss" text="Duplicated canonical URL"
        xmlUrl="https://example.com/feed#fragment"/>
      <outline type="rss" text="Science" xmlUrl="https://science.example.org/rss?q=a&amp;lang=de"/>
    </outline>
  </body>
</opml>"""


def test_opml_nested_feeds_are_proposals_deduplicated_in_order():
    feeds = parse_opml(sample_opml())
    assert [f.title for f in feeds] == ["Example & Co", "Science"]
    assert len(feeds) == 2
    assert all(f.mode == "reference-only" and f.enabled is False for f in feeds)
    assert proposal_document(feeds)["state"] == "proposed-only"


def test_opml_round_trip_does_not_activate():
    original = parse_opml(sample_opml())
    exported = render_opml(original)
    assert b"Example &amp; Co" in exported
    newer = parse_opml(exported)
    assert [f.to_dict() for f in original] == [f.to_dict() for f in newer]


@pytest.mark.parametrize(
    "payload",
    [
        b"<opml version='2.0'><body>",
        b"<!DOCTYPE opml [<!ENTITY x SYSTEM 'file:///etc/passwd'>]><opml version='2.0'/>",
        b"<opml version='2.0'><body><outline xmlUrl='file:///etc/passwd'/></body></opml>",
        b"<opml version='2.0'><body><outline xmlUrl='https://u:pass@example.org/a'/></body></opml>",
        b"<opml version='2.0'><body><outline xmlUrl='javascript:alert(1)'/></body></opml>",
        b"<opml version='2.0'><body><outline xmlUrl='http://bad host/a'/></body></opml>",
        b"<opml version='2.0'><body><outline xmlUrl='https://example.org:99999/rss'/></body></opml>",
        b"<html><body /></html>",
        b"<opml version='2.0'></opml>",
        b"x" * 1_048_577,
    ],
)
def test_reject_unsafe_or_invalid_opml(payload):
    with pytest.raises(OPMLImportError):
        parse_opml(payload)


def test_stops_more_than_500_distinct_feeds():
    outlines = "".join(
        f"<outline xmlUrl='https://example.org/rss/{i}'/>" for i in range(501)
    )
    with pytest.raises(OPMLImportError, match="500"):
        parse_opml(f"<opml version='2.0'><body>{outlines}</body></opml>".encode())


def test_private_output_and_no_overwrite(tmp_path):
    feeds = parse_opml(sample_opml())
    path = tmp_path / "proposal.json"
    write_proposal(path, feeds)
    doc = json.loads(path.read_text())
    assert doc["feeds"][0]["enabled"] is False
    assert doc["activation"] == "requires-explicit-user-approval"
    if os.name != "nt":
        assert path.stat().st_mode & 0o777 == 0o600
    assert read_proposal(path) == feeds
    with pytest.raises(OPMLImportError, match="exists"):
        write_proposal(path, feeds)


def test_tampered_enabled_feed_rejected_by_export(tmp_path):
    path = tmp_path / "proposal.json"
    doc = proposal_document(parse_opml(sample_opml()))
    doc["feeds"][0]["enabled"] = True
    path.write_text(json.dumps(doc))
    with pytest.raises(OPMLImportError, match="approval"):
        read_proposal(path)


def test_cli_import_preview_and_export_are_offline(tmp_path, monkeypatch, capsys):
    def fail_network(*args, **kwargs):
        raise AssertionError("OPML must never fetch URLs")
    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", fail_network)
    opml = tmp_path / "input.opml"
    opml.write_bytes(sample_opml())
    proposal = tmp_path / "unactivated.json"
    output = tmp_path / "reexport.opml"
    assert main(["sources-import-opml", str(opml)]) == 0
    preview = json.loads(capsys.readouterr().out)
    assert preview == {
        "status": "proposed-only", "feed_count": 2,
        "activated": 0, "network_requests": 0, "output": None,
    }
    assert main(["sources-import-opml", str(opml), "--output", str(proposal)]) == 0
    assert json.loads(capsys.readouterr().out)["activated"] == 0
    assert main(["sources-export-opml", str(proposal), "--output", str(output)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "exported"
    assert report["network_requests"] == 0
    assert len(parse_opml(output.read_bytes())) == 2


def test_rejected_cli_input_has_no_side_effects(tmp_path, capsys):
    opml = tmp_path / "unsafe.opml"
    opml.write_text(
        "<!DOCTYPE x><opml version='2.0'><body /></opml>", encoding="utf-8"
    )
    proposal = tmp_path / "proposal.json"
    assert main(["sources-import-opml", str(opml), "--output", str(proposal)]) == 2
    assert not proposal.exists()
    response = json.loads(capsys.readouterr().out)
    assert response["status"] == "rejected"
    assert "DOCTYPE" not in response["error"]


def test_bad_proposal_export_never_overwrites_existing_path(tmp_path):
    a = tmp_path / "proposal.json"
    write_proposal(a, parse_opml(sample_opml()))
    existing = tmp_path / "existing.opml"
    existing.write_text("previous owner artifact", encoding="utf-8")
    with pytest.raises(OPMLImportError, match="exists"):
        from kushluk.opml import write_private_file
        write_private_file(existing, render_opml(read_proposal(a)))
    assert existing.read_text() == "previous owner artifact"
