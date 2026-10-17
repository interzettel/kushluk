"""Conservative, read-only archived edition compatibility contract tests."""
from __future__ import annotations

from datetime import date
import json

import pytest

from kushluk.archive_compat import ArchiveCompatError, inspect_archive_root
from kushluk.cli import main
from kushluk.preview import frozen_publication


def _write(root, key="20261017-001", payload=None):
    path = root / key
    path.mkdir(parents=True)
    if payload is None:
        payload = frozen_publication().to_dict()
    (path / "metadata.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8",
    )
    return path


def test_compatible_v2_archive_report_has_no_user_content(tmp_path):
    root = tmp_path / "private-archives"
    original = frozen_publication().to_dict()
    original["location_name"] = "Private address with token=SUPER_SECRET"
    folder = _write(root, payload=original)
    prior = (folder / "metadata.json").read_bytes()
    result = inspect_archive_root(root)
    assert result == {
        "schema_version": 1, "checked": 1, "total_found": 1,
        "truncated": False, "categories": {"readable_v2_metadata": 1},
        "migration_performed": False, "delivery_approved": False,
    }
    assert "SUPER_SECRET" not in json.dumps(result)
    assert (folder / "metadata.json").read_bytes() == prior


def test_legacy_v1_future_schema_and_invalid_v2_require_explicit_review(tmp_path):
    root = tmp_path / "archive"
    _write(root, key="20261017-001", payload={"schema_version": 1})
    future = frozen_publication().to_dict()
    future["schema_version"] = 300
    _write(root, key="20261018-001", payload=future)
    broken = frozen_publication().to_dict()
    broken["edition_id"] = "20261019-001"
    broken["target_date"] = "2026-10-19"
    broken["pages"][1]["story_ids"] = ["missing-story"]
    _write(root, key="20261019-001", payload=broken)
    result = inspect_archive_root(root)
    assert result["categories"] == {
        "invalid_v2_references": 1,
        "legacy_v1_requires_migration": 1,
        "unsupported_schema": 1,
    }
    assert result["migration_performed"] is False


def test_symlinks_missing_malformed_oversize_fail_closed(tmp_path):
    root = tmp_path / "archive"
    invalid = root / "20261017-001"
    invalid.mkdir(parents=True)
    (invalid / "metadata.json").write_text("{broken")
    missing = root / "20261018-001"
    missing.mkdir()
    oversized = root / "20261019-001"
    oversized.mkdir()
    (oversized / "metadata.json").write_bytes(b" " * (2 * 1024 * 1024 + 1))
    pointed = root / "20261020-001"
    pointed.mkdir()
    (pointed / "metadata.json").symlink_to(invalid / "metadata.json")
    linked = root / "20261021-001"
    linked.symlink_to(invalid, target_is_directory=True)
    categories = inspect_archive_root(root)["categories"]
    assert categories == {
        "invalid_metadata_json": 1, "missing_metadata": 1,
        "oversized_metadata": 1, "unsafe_archive_metadata": 1,
        "unsafe_archive_path": 1,
    }


def test_compatibility_scan_is_bounded_and_reports_truncation(tmp_path, capsys):
    root = tmp_path / "archive"
    _write(root, key="20261017-001")
    _write(root, key="20261018-001")
    result = inspect_archive_root(root, limit=1)
    assert result["checked"] == 1 and result["total_found"] == 2
    assert result["truncated"]
    assert main(["archive-check", "--archive-root", str(root), "--limit", "1"]) == 1
    public = json.loads(capsys.readouterr().out)
    assert public["truncated"] is True
    assert public["delivery_approved"] is False


def test_archive_root_symlink_rejected_and_empty_is_safe(tmp_path):
    root = tmp_path / "archive"
    assert inspect_archive_root(root)["categories"] == {}
    root.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(root, target_is_directory=True)
    with pytest.raises(ArchiveCompatError, match="unsafe_archive_root"):
        inspect_archive_root(alias)
    with pytest.raises(ArchiveCompatError, match="invalid_compat_limit"):
        inspect_archive_root(root, limit=0)


def test_archive_check_matches_v2_fields_not_pdf_quality(tmp_path):
    root = tmp_path / "private"
    _write(root)
    report = inspect_archive_root(root)
    assert report["categories"]["readable_v2_metadata"] == 1
    assert report["delivery_approved"] is False
    # The check never invokes CUPS, PDFs, network or migrations.
