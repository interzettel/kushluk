"""Offline licence-review worksheet tests: metadata is evidence, not signoff."""
from __future__ import annotations

from hashlib import sha256
import json

import pytest

from tools import license_review_matrix as review


def python_inventory():
    return {
        "schema_version": 1, "kind": "installed-python-environment-inventory",
        "installed_packages": [
            {"name": "kushluk", "version": "0.1.0",
             "license_metadata_status": "legacy_license_field_only"},
            {"name": "jinja2", "version": "3.1.6",
             "license_metadata_status": "license_expression_declared"},
            {"name": "httpx", "version": "0.28.1",
             "license_metadata_status": "license_classifier_only"},
        ],
    }


def native_inventory():
    return {
        "schema_version": 1, "kind": "native-print-dependency-observation",
        "native_library_versions": {
            "pango": "1.58.2", "cairo": "1.18.4",
            "harfbuzz": "14.3.1", "fontconfig": "2.18.3",
        },
        "font_family_matches": {
            "serif": "PRIVATE_FONT_PASSWORD", "sans-serif": "Verdana",
            "monospace": "Andale Mono",
        },
        "font_licenses_reviewed": False,
    }


def test_sorted_review_gaps_and_metadata_are_not_legal_approval():
    result = review.build_matrix(python_inventory(), native=native_inventory())
    assert [x["package"] for x in result["python_environment_packages"]] == [
        "httpx", "jinja2", "kushluk",
    ]
    assert result["review_counts"]["packages_missing_modern_license_expression"] == 2
    assert result["review_counts"]["python_pending"] == 3
    assert result["review_counts"]["native_pending"] == 4
    assert result["review_counts"]["font_pending"] == 3
    assert result["signoffs"]["font_embedding_and_redistribution"] is False
    assert result["approved_for_release"] is False
    assert "PRIVATE_FONT_PASSWORD" not in json.dumps(result)
    assert result["native_libraries"][-1]["observed_version"] == "1.58.2"


def test_native_optional_keeps_unresolved_items_explicit():
    result = review.build_matrix(python_inventory())
    assert result["review_counts"]["native_environment_observed"] is False
    assert all(row["observed_version"] is None for row in result["native_libraries"])
    assert all(row["embedding_rights_verified"] is False for row in result["font_matches"])


@pytest.mark.parametrize("packages", [
    [], [{"name": "kushluk", "version": "0.1.0",
          "license_metadata_status": "not_reviewed_by_security_tool"}],
    [{"name": "kushluk", "version": "0.1.0",
      "license_metadata_status": "legacy_license_field_only"}] * 2,
    [{"name": "kushluk", "version": "0.1.0\nSECRET",
      "license_metadata_status": "legacy_license_field_only"}],
])
def test_bad_inventory_rejected(packages):
    inventory = python_inventory()
    inventory["installed_packages"] = packages
    with pytest.raises(review.ReviewMatrixError):
        review.build_matrix(inventory)


def test_cli_creates_only_new_private_worksheet_and_digests_sources(
    tmp_path, capsys,
):
    py = tmp_path / "python.json"
    native = tmp_path / "native.json"
    py.write_text(json.dumps(python_inventory()), encoding="utf-8")
    native.write_text(json.dumps(native_inventory()), encoding="utf-8")
    output = tmp_path / "private" / "licences.json"
    assert review.main(["--python", str(py), "--native", str(native),
                        "--output", str(output)]) == 0
    observed = json.loads(output.read_text())
    assert observed["python_inventory_sha256"] == sha256(py.read_bytes()).hexdigest()
    assert observed["native_inventory_sha256"] == sha256(native.read_bytes()).hexdigest()
    assert observed["approved_for_release"] is False
    assert "PRIVATE_FONT_PASSWORD" not in output.read_text()
    assert output.stat().st_mode & 0o777 == 0o600
    assert json.loads(capsys.readouterr().out)["signoff_complete"] is False
    unchanged = output.read_bytes()
    assert review.main(["--python", str(py), "--output", str(output)]) == 2
    assert output.read_bytes() == unchanged


def test_cli_rejects_untrusted_source_links_and_public_parent(tmp_path, capsys):
    py = tmp_path / "input.json"
    py.write_text(json.dumps(python_inventory()))
    link = tmp_path / "link.json"
    link.symlink_to(py)
    assert review.main(["--python", str(link),
                        "--output", str(tmp_path / "out.json")]) == 2
    assert not (tmp_path / "out.json").exists()
    public = tmp_path / "public"
    public.mkdir(mode=0o755)
    assert review.main(["--python", str(py),
                        "--output", str(public / "out.json")]) == 2
    assert not (public / "out.json").exists()


def test_unknown_native_metadata_sanitized_without_raw_paths():
    native = native_inventory()
    native["native_library_versions"]["pango"] = "/private/path/SECRET"
    result = review.build_matrix(python_inventory(), native=native)
    assert result["native_libraries"][-1]["observed_version"] is None
    assert "SECRET" not in json.dumps(result)
