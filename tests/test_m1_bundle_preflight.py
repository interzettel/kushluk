"""Offline M1 artifact-bundle validation, never release approval."""
from __future__ import annotations

from hashlib import sha256
import json

import pytest

from tools.m1_bundle_preflight import M1EvidenceError, inspect_bundle, main


def _digest(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True).encode("utf-8")
    path.write_bytes(data)
    return _digest(data)


def _make_bundle(tmp_path, *, pdf=False, drift=False):
    folder = tmp_path / "bundle"
    version = "0.1.0"
    wheel = f"kushluk-{version}-py3-none-any.whl"
    sdist = f"kushluk-{version}.tar.gz"
    whash = _write(folder / wheel, b"fictional-wheel-bytes")
    shash = _write(folder / sdist, b"fictional-sdist-bytes")
    archive = {}
    preview = {
        "kushluk-preview.html": b"<html>fictional editorial sample</html>",
        "kushluk-preview.md": b"# Fictional paper",
        "kushluk-preview-edition.json": b'{"schema_version":2}',
    }
    if pdf:
        preview["kushluk-preview.pdf"] = b"%PDF fictional unit fixture"
    for key, name in (("wheel", wheel), ("sdist", sdist)):
        root = folder / key
        installed = {
            "schema_version": 1, "kind": "installed-python-environment-inventory",
            "installed_packages": [
                {"name": "kushluk", "version": "0.1.0"},
                {"name": "jinja2", "version": "3.1.6"},
            ],
            "legal_license_review_complete": False,
        }
        inv_hash = _write(root / "installed-environment.json", installed)
        worksheet = {
            "schema_version": 1, "kind": "license-review-evidence-worksheet",
            "human_signoff_required": True, "approved_for_release": False,
            "python_inventory_sha256": inv_hash,
            "review_counts": {"python_pending": 2},
        }
        worksheet_hash = _write(root / "license-review-worksheet.json", worksheet)
        file_hashes = {}
        for filename, contents in preview.items():
            b = contents + (b"-drift" if drift and key == "sdist" else b"")
            file_hashes[filename] = _write(root / filename, b)
        manifest = {
            "schema_version": 1, "fixture_date": "2026-10-17",
            "fixture_generated_at": "2026-10-17T07:00:00+02:00",
            "four_logical_a4_pages": True, "pdf_validated": pdf,
            "network_requests": 0, "printer_submissions": 0,
            "mail_submissions": 0, "synthetic_only": True,
            "physical_verified": False, "files": file_hashes,
        }
        _write(root / "preview-manifest.json", manifest)
        archive[key] = {
            "installed_distribution": name,
            "runtime_module_from_venv": True,
            "synthetic_only": True, "physical_verified": False,
            "pdf_validated": pdf, "license_signoff_complete": False,
            "legal_license_review_complete": False,
            "dependency_count": 2,
            "dependency_inventory": "installed-environment.json",
            "dependency_inventory_sha256": inv_hash,
            "license_review_worksheet": "license-review-worksheet.json",
            "license_review_worksheet_sha256": worksheet_hash,
            "files": file_hashes,
        }
    evidence = {
        "schema_version": 1, "status": "clean_install_passed",
        "development_version": version,
        "suggested_prerelease": "v0.2.0-alpha.1",
        "tag_created": False, "published": False,
        "builds_byte_reproducible": True,
        "installed_dependency_inventory_available": True,
        "legal_license_review_complete": False,
        "native_dependency_review_complete": False,
        "pdf_validated": pdf, "physical_verified": False,
        "network_used_by_preview": False,
        "wheel_sha256": whash, "sdist_sha256": shash,
        "installs": archive,
    }
    _write(folder / "release-evidence.json", evidence)
    return folder


@pytest.mark.parametrize("pdf", [False, True])
def test_verified_software_bundle_still_blocks_release(tmp_path, pdf):
    folder = _make_bundle(tmp_path, pdf=pdf)
    report = inspect_bundle(folder, require_pdf=pdf)
    assert report["status"] == "software_evidence_ready_for_review"
    assert report["installed_version"] == "0.1.0"
    assert report["proposed_release_tag"] == "v0.2.0-alpha.1"
    assert report["release_authorized"] is False
    assert report["legal_license_signoff_complete"] is False
    assert report["physical_print_and_host_verified"] is False
    assert report["tag_created_by_preflight"] is False


def test_cli_prints_only_content_free_release_recommendation(tmp_path, capsys):
    folder = _make_bundle(tmp_path)
    assert main(["--artifact-dir", str(folder)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["sample_network_print_email_submissions"] == 0
    assert result["release_authorized"] is False
    assert not (folder / "release-approval.json").exists()


def test_rejects_modified_distribution_without_echoing_private_input(tmp_path, capsys):
    folder = _make_bundle(tmp_path)
    with (folder / "kushluk-0.1.0-py3-none-any.whl").open("ab") as out:
        out.write(b"PRIVATE_USER_PASSWORD")
    assert main(["--artifact-dir", str(folder)]) == 2
    raw = capsys.readouterr().out
    assert "artifact_checksum_mismatch" in raw
    assert "PRIVATE_USER_PASSWORD" not in raw


def test_rejects_modified_synthetic_page(tmp_path):
    folder = _make_bundle(tmp_path)
    (folder / "wheel" / "kushluk-preview.html").write_text("Tampered")
    with pytest.raises(M1EvidenceError, match="checksum"):
        inspect_bundle(folder)


def test_rejects_rewritten_license_signoff_and_unsafe_symlink(tmp_path):
    folder = _make_bundle(tmp_path)
    evidence = json.loads((folder / "release-evidence.json").read_text())
    evidence["tag_created"] = True
    _write(folder / "release-evidence.json", evidence)
    with pytest.raises(M1EvidenceError, match="unsupported"):
        inspect_bundle(folder)
    evidence["tag_created"] = False
    _write(folder / "release-evidence.json", evidence)
    original = folder / "wheel" / "installed-environment.json"
    contents = original.read_bytes()
    original.unlink()
    destination = tmp_path / "private-secret"
    destination.write_bytes(contents)
    original.symlink_to(destination)
    with pytest.raises(M1EvidenceError, match="unsafe"):
        inspect_bundle(folder)


def test_cross_install_drift_fails_even_with_valid_matching_own_hashes(tmp_path):
    folder = _make_bundle(tmp_path, drift=True)
    with pytest.raises(M1EvidenceError, match="drift"):
        inspect_bundle(folder)


def test_rejects_pdf_requirement_and_any_outbound_claim(tmp_path):
    folder = _make_bundle(tmp_path, pdf=False)
    with pytest.raises(M1EvidenceError, match="unverified"):
        inspect_bundle(folder, require_pdf=True)
    manifest = folder / "wheel" / "preview-manifest.json"
    record = json.loads(manifest.read_text())
    record["network_requests"] = 1
    _write(manifest, record)
    with pytest.raises(M1EvidenceError, match="manifest"):
        inspect_bundle(folder)
