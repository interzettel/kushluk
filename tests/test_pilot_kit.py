"""Blank offline pilot kits must be private, schema-compatible, and never approvals."""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path

import pytest

from kushluk.cli import main
from kushluk.pilot_kit import PilotKitError, create_pilot_kit
from tools.accessibility_evidence import assess as check_accessibility
from tools.first_reader_evidence import assess as check_first_reader
from tools.beta_pilot_preflight import inspect_safety, BetaEvidenceError


FILES = {
    "MANIFEST.json", "SESSION.md", "safety.json", "first-reader.json",
    "accessibility.json",
}


def _read(directory: Path, name: str) -> dict:
    return json.loads((directory / name).read_text(encoding="utf-8"))


def test_blank_private_kit_matches_canonical_templates(tmp_path):
    target = tmp_path / "private-kit"
    result = create_pilot_kit(target, source_commit="a" * 40)
    assert result["status"] == "private_blank_pilot_kit_created"
    assert result["files_created"] == 5
    assert not result["beta_publication_authorized"]
    assert {p.name for p in target.iterdir()} == FILES
    if os.name != "nt":
        assert target.stat().st_mode & 0o777 == 0o700
        for path in target.iterdir():
            assert path.stat().st_mode & 0o777 == 0o600
    for name, reference in (
        ("first-reader.json", "FIRST_READER_TEMPLATE.json"),
        ("accessibility.json", "ACCESSIBILITY_TEMPLATE.json"),
        ("safety.json", "BETA_PILOT_SAFETY_TEMPLATE.json"),
    ):
        canonical = json.loads((Path("docs") / reference).read_text())
        actual = _read(target, name)
        if "source_commit" in canonical:
            canonical["source_commit"] = "a" * 40
        assert actual == canonical
    manifest = _read(target, "MANIFEST.json")
    assert manifest["source_commit"] == "a" * 40
    assert manifest["source_commit_verified_against_installation"] is False
    assert manifest["beta_publication_authorized"] is False
    assert manifest["release_gates_independently_verified"] == 0
    assert set(manifest["files_sha256"]) == FILES - {"MANIFEST.json"}
    for name, digest in manifest["files_sha256"].items():
        assert sha256((target / name).read_bytes()).hexdigest() == digest
    assert check_first_reader(_read(target, "first-reader.json"))["status"] == "template"
    assert check_accessibility(_read(target, "accessibility.json"))["status"] == "template"
    with pytest.raises(BetaEvidenceError):
        inspect_safety(target / "safety.json")


def test_cli_without_commit_creates_only_unverified_templates(tmp_path, capsys):
    out = tmp_path / "blank"
    assert main(["pilot-kit", "--output-dir", str(out)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "private_blank_pilot_kit_created"
    assert "source_commit_verified" in report
    assert report["source_commit_verified"] is False
    assert str(out) not in json.dumps(report)
    assert _read(out, "first-reader.json")["source_commit"] == (
        "REPLACE_WITH_TESTED_MAIN_COMMIT"
    )
    session = (out / "SESSION.md").read_text()
    assert "five genuine unattended mornings" in session
    assert "NOT a real observed trial" in session
    assert "No actual hardware" in session


def test_refuse_existing_dir_without_modifying_anything(tmp_path):
    out = tmp_path / "existing"
    out.mkdir()
    marker = out / "private.json"
    marker.write_bytes(b"secret not to be touched")
    with pytest.raises(PilotKitError, match="must_be_new"):
        create_pilot_kit(out)
    assert marker.read_bytes() == b"secret not to be touched"
    assert sorted(p.name for p in out.iterdir()) == ["private.json"]


@pytest.mark.parametrize("bad", [
    "main", "a" * 39, "a" * 41, "A" * 40, "a" * 39 + "/",
])
def test_refuse_invalid_commit_before_creating_file(tmp_path, bad):
    folder = tmp_path / "uncreated"
    with pytest.raises(PilotKitError, match="invalid_source_commit"):
        create_pilot_kit(folder, source_commit=bad)
    assert not folder.exists()


def test_refuse_parent_or_destination_symlink(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    parent_alias = tmp_path / "parent-link"
    parent_alias.symlink_to(real, target_is_directory=True)
    with pytest.raises(PilotKitError, match="must_be_new"):
        create_pilot_kit(parent_alias / "pilot")
    assert not (real / "pilot").exists()
    target_alias = tmp_path / "target-link"
    target_alias.symlink_to(real, target_is_directory=True)
    with pytest.raises(PilotKitError, match="must_be_new"):
        create_pilot_kit(target_alias)
    assert not (real / "MANIFEST.json").exists()


def test_cli_bad_sha_sanitizes_return_and_never_makes_private_files(tmp_path, capsys):
    folder = tmp_path / "never-created"
    assert main([
        "pilot-kit", "--output-dir", str(folder),
        "--source-commit", "MY_PRIVATE_INFORMATION",
    ]) == 2
    output = capsys.readouterr().out
    assert "MY_PRIVATE_INFORMATION" not in output
    assert str(folder) not in output
    assert not folder.exists()


def test_generating_pilot_kit_does_not_touch_external_devices(tmp_path, monkeypatch):
    import subprocess
    import socket

    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: pytest.fail("subprocess"))
    monkeypatch.setattr(socket, "create_connection",
                        lambda *a, **kw: pytest.fail("network"))
    report = create_pilot_kit(tmp_path / "test-kit")
    assert report["status"] == "private_blank_pilot_kit_created"
    assert report["physical_print_verified"] is False
    assert report["first_reader_verified"] is False


def test_canonicalizes_ancestor_alias_but_refuses_missing_parent(tmp_path):
    private = tmp_path / "private"
    private.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(private, target_is_directory=True)
    # A macOS /var-style ancestor alias is resolved BEFORE any writes.
    # The resulting private 0700 kit is at a canonical filesystem location.
    nested = alias / "nested"
    nested.mkdir()
    create_pilot_kit(nested / "kit")
    assert (private / "nested" / "kit" / "MANIFEST.json").is_file()
    assert (private / "nested" / "kit").stat().st_mode & 0o777 == 0o700
    with pytest.raises(PilotKitError, match="parent_invalid"):
        create_pilot_kit(tmp_path / "nonexistent" / "kit")
    assert not (tmp_path / "nonexistent").exists()


def test_failed_write_removes_only_own_partial_kit(tmp_path, monkeypatch):
    import kushluk.pilot_kit as module

    marker = tmp_path / "operator-notes.txt"
    marker.write_text("private operator text", encoding="utf-8")
    real_create = module._create_file

    def fail_on_safety(path, blob):
        if path.name == "safety.json":
            raise OSError("PRIVATE_PATH_AND_CONTENT_MUST_NOT_LEAK")
        return real_create(path, blob)

    monkeypatch.setattr(module, "_create_file", fail_on_safety)
    out = tmp_path / "partial"
    with pytest.raises(PilotKitError, match="private_kit_creation_failed") as exc:
        create_pilot_kit(out)
    assert "PRIVATE_PATH_AND_CONTENT" not in str(exc.value)
    assert not out.exists()
    assert marker.read_text(encoding="utf-8") == "private operator text"
