"""Read-only field receipt summary must not grant hardware acceptance."""
from datetime import datetime, timedelta, timezone
import json

from tools.field_receipt_audit import audit_receipts


def receipt(day, kind="host-resume", result="pass"):
    return {
        "schema_version": 1, "kind": kind, "operator_reported_result": result,
        "observed_at_utc": day.isoformat(),
        "artifact": {"sha256": "a" * 64, "bytes": 10},
        "print_inspection_sha256": "b" * 64 if kind.startswith("paper-") else None,
        "evidence_files": [{"sha256": "c" * 64, "bytes": 12}],
        "acknowledged_direct_observation": True,
        "attestation": "operator-self-report; not independently validated",
        "independently_verified": False, "release_gate_accepted": False,
        "device_description": "PRIVATE DEVICE", "operator_identifier": "PRIVATE PERSON",
        "observations": "PRIVATE OBSERVATION",
    }


def test_five_distinct_days_are_still_unverified(tmp_path):
    base = datetime(2026, 10, 1, tzinfo=timezone.utc)
    for n in range(5):
        (tmp_path / f"{n}.json").write_text(json.dumps(receipt(base + timedelta(days=n))))
    result = audit_receipts(tmp_path)
    assert result["host_five_distinct_utc_dates_reported"] is True
    assert result["independently_verified"] is False
    assert result["release_gate_accepted"] is False
    assert "PRIVATE" not in json.dumps(result)


def test_duplicates_invalid_and_forged_approval_are_not_counted(tmp_path):
    base = datetime(2026, 10, 1, tzinfo=timezone.utc)
    for n in range(2):
        (tmp_path / f"repeat-{n}.json").write_text(json.dumps(receipt(base)))
    fake = receipt(base)
    fake["release_gate_accepted"] = True
    (tmp_path / "forged.json").write_text(json.dumps(fake))
    (tmp_path / "broken.json").write_text("{")
    (tmp_path / "linked.json").symlink_to(tmp_path / "repeat-0.json")
    result = audit_receipts(tmp_path)
    assert result["host_reported_pass_utc_dates"] == 1
    assert result["operator_reports"]["host-resume"]["pass"] == 2
    assert result["invalid_or_unsupported_entries"] == 3
    assert result["host_five_distinct_utc_dates_reported"] is False


def test_paper_pass_requires_inspection_and_evidence(tmp_path):
    sample = receipt(datetime(2026, 10, 1, tzinfo=timezone.utc), kind="paper-a4")
    sample["print_inspection_sha256"] = None
    (tmp_path / "untrusted.json").write_text(json.dumps(sample))
    assert audit_receipts(tmp_path)["invalid_or_unsupported_entries"] == 1
