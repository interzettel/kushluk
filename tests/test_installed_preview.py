"""Installed-preview contract. All content is original synthetic fixture data."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import socket

import pytest

from kushluk.cli import main
from kushluk.preview import PreviewError, frozen_publication, make_preview
from kushluk.validation import validate_publication


def test_fixture_has_stable_story_and_page_identities():
    a, b = frozen_publication(), frozen_publication()
    assert a.to_dict() == b.to_dict()
    assert a.generated_at == "2026-10-17T07:00:00+02:00"
    assert a.edition_id == "20261017-001"
    assert [p.kind for p in a.pages] == ["front", "day", "stories", "sources"]
    assert all("synthetic" in s.source_name.lower() for s in a.stories)
    assert all(s.source_url is None for s in a.stories)
    assert validate_publication(a).ok


def test_cli_offline_preview_does_not_use_settings_or_network(tmp_path, monkeypatch, capsys):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("The installed preview must remain strictly offline")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr("kushluk.config.Settings.from_env", forbidden)
    monkeypatch.setattr("kushluk.pipeline.run_pipeline", forbidden)
    monkeypatch.setattr("kushluk.pipeline.print_pdf", forbidden)
    monkeypatch.setattr("kushluk.pipeline.send_email_edition", forbidden)
    path = tmp_path / "edition"
    assert main(["preview", "--output-dir", str(path)]) == 0
    response = json.loads(capsys.readouterr().out)
    assert response == {
        "status": "synthetic_preview_created", "logical_pages": 4,
        "pdf_validated": False, "synthetic_only": True,
        "physical_verified": False, "network_requests": 0,
        "delivery_submissions": 0,
    }
    manifest = json.loads((path / "preview-manifest.json").read_text())
    assert manifest["network_requests"] == 0
    assert manifest["printer_submissions"] == 0
    assert manifest["mail_submissions"] == 0
    assert manifest["physical_verified"] is False
    assert manifest["fixture_generated_at"] == "2026-10-17T07:00:00+02:00"
    assert len(manifest["files"]) == 3
    for name, digest in manifest["files"].items():
        assert sha256((path / name).read_bytes()).hexdigest() == digest
    assert "SYNTHETIC EDITION" in (path / "kushluk-preview.html").read_text()


def test_two_frozen_previews_have_identical_text_and_metadata(tmp_path):
    first = make_preview(tmp_path / "a")
    second = make_preview(tmp_path / "b")
    assert first == second
    assert (tmp_path / "a" / "kushluk-preview.html").read_bytes() == (
        tmp_path / "b" / "kushluk-preview.html").read_bytes()


def test_prevents_accidental_preview_overwrite_and_symlink(tmp_path):
    directory = tmp_path / "filled"
    directory.mkdir()
    (directory / "personal.txt").write_text("keep this private")
    with pytest.raises(PreviewError, match="preview_destination_not_empty"):
        make_preview(directory)
    assert (directory / "personal.txt").read_text() == "keep this private"
    symlink = tmp_path / "link"
    symlink.symlink_to(directory, target_is_directory=True)
    with pytest.raises(PreviewError, match="unsafe_preview_destination"):
        make_preview(symlink)
    assert main(["preview", "--output-dir", str(directory)]) == 2


def test_pdf_preview_has_four_logical_a4_pages_without_devices(tmp_path):
    pytest.importorskip("weasyprint")
    pytest.importorskip("pypdf")
    from kushluk.validation import validate_pdf
    output = tmp_path / "pdf"
    manifest = make_preview(output, pdf=True)
    assert manifest["pdf_validated"] is True
    assert "kushluk-preview.pdf" in manifest["files"]
    check = validate_pdf(output / "kushluk-preview.pdf", expected_pages=4)
    assert check.ok, check.errors


def test_pdf_dependency_failure_does_not_create_partial_preview(tmp_path, monkeypatch):
    import builtins
    original = builtins.__import__

    def block(name, *args, **kwargs):
        if name == "pypdf":
            raise ImportError("unavailable optional PDF module")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", block)
    target = tmp_path / "no-pdf"
    with pytest.raises(PreviewError, match="pdf_dependencies_required"):
        make_preview(target, pdf=True)
    assert not target.exists()
