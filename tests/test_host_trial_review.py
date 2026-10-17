"""Host trial review correlates local receipts; it never proves unattended delivery."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
import json

from kushluk.cli import main
from kushluk.host_trial_review import HostTrialReviewError, review_host_trial
import pytest


BASE = date(2026, 10, 1)


def make_day(root, day, *, validated=True, expected_start="07:30"):
    folder = root / f"{day:%Y%m%d}-001"
    folder.mkdir(parents=True, exist_ok=True)
    start = datetime(day.year, day.month, day.day, 5, 30, tzinfo=timezone.utc)
    def stamp(minutes):
        return (start + timedelta(minutes=minutes)).isoformat()
    events = [{"stage": "started", "at": stamp(0)}]
    if validated:
        events.extend([
            {"stage": "validated", "at": stamp(2)},
            {"stage": "archive_ready", "at": stamp(3)},
        ])
    events.append({"stage": "complete", "at": stamp(4)})
    record = {
        "schema_version": 1, "edition_id": folder.name, "status": "completed",
        "stage": "complete", "started_at": stamp(0), "finished_at": stamp(4),
        "stage_events": events, "stages": [row["stage"] for row in events],
        "failure_codes": [], "expected_start_local": expected_start,
        "ready_by_local": "08:00",
        "request": {"send_to_printer": False, "send_email": False,
                    "email_on_print_failure": False, "print_profile": "a4-home"},
        "print_submitted": False, "email_sent": False,
    }
    path = folder / "scheduled.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return path


def make_attestation(receipts_dir, artifact, *, name, stamp=None):
    content = artifact.read_bytes()
    finish = datetime.fromisoformat(json.loads(content)["finished_at"])
    data = {
        "schema_version": 1, "kind": "host-resume",
        "operator_reported_result": "pass",
        "observed_at_utc": (stamp or (finish + timedelta(minutes=5))).isoformat(),
        "artifact": {"sha256": sha256(content).hexdigest(), "bytes": len(content)},
        "evidence_files": [{"sha256": "b" * 64, "bytes": 123}],
        "acknowledged_direct_observation": True,
        "attestation": "operator-self-report; not independently validated",
        "independently_verified": False, "release_gate_accepted": False,
        "operator_identifier": "private tester", "device_description": "private printer",
        "observations": "private note: secret-case-888",
    }
    (receipts_dir / name).write_text(json.dumps(data), encoding="utf-8")
    return data


def test_five_consecutive_local_run_receipts_pair_but_do_not_verify_host(tmp_path):
    archive = tmp_path / "archive"
    receipts = tmp_path / "evidence"
    receipts.mkdir()
    for index in range(5):
        day = BASE + timedelta(days=index)
        path = make_day(archive, day)
        make_attestation(receipts, path, name=f"proof-{index}.json")
    summary = review_host_trial(archive_root=archive, receipts_dir=receipts,
                                start_date=BASE)
    assert summary["days_with_matching_operator_host_reports"] == 5
    assert summary["days_with_matching_reports_and_recorded_expected_start"] == 5
    assert summary["all_trial_days_have_matching_reports"] is True
    assert all(d["software_ready_by_target"] for d in summary["days"])
    assert summary["unattended_host_verified"] is False
    assert summary["physical_print_verified"] is False
    assert summary["release_gate_accepted"] is False
    assert "secret-case-888" not in json.dumps(summary)
    assert "private printer" not in json.dumps(summary)


def test_missing_date_and_mismatching_artifact_fail_closed(tmp_path):
    archive = tmp_path / "archive"
    receipts = tmp_path / "evidence"
    receipts.mkdir()
    path = make_day(archive, BASE)
    proof = make_attestation(receipts, path, name="one.json")
    proof["artifact"]["sha256"] = "f" * 64
    (receipts / "one.json").write_text(json.dumps(proof))
    review = review_host_trial(archive_root=archive, receipts_dir=receipts,
                               start_date=BASE)
    assert review["days_with_matching_operator_host_reports"] == 0
    assert review["unmatched_or_out_of_window_host_reports"] == 1
    assert review["days_with_validated_software_archives"] == 1
    assert not review["days"][1]["run_receipt_readable"]


def test_invalid_approvals_symlinks_and_missing_validation_fail_closed(tmp_path):
    archive = tmp_path / "archive"
    receipts = tmp_path / "receipts"
    receipts.mkdir()
    path = make_day(archive, BASE, validated=False)
    proof = make_attestation(receipts, path, name="forged.json")
    proof["independently_verified"] = True
    (receipts / "forged.json").write_text(json.dumps(proof))
    (receipts / "link.json").symlink_to(receipts / "forged.json")
    result = review_host_trial(archive_root=archive, receipts_dir=receipts,
                               start_date=BASE)
    assert result["invalid_or_unsupported_receipts"] == 2
    assert not result["days"][0]["software_completed_with_validated_archive"]
    assert not result["days"][0]["matching_operator_host_pass_reported"]



def test_legitimate_failed_and_paper_proofs_are_not_malformed(tmp_path):
    archive = tmp_path / "archive"
    receipts = tmp_path / "receipts"
    receipts.mkdir()
    path = make_day(archive, BASE)
    failure = make_attestation(receipts, path, name="failed.json")
    failure["operator_reported_result"] = "fail"
    (receipts / "failed.json").write_text(json.dumps(failure))
    paper = dict(failure)
    paper["kind"] = "paper-a4"
    paper["operator_reported_result"] = "pass"
    paper["print_inspection_sha256"] = "a" * 64
    (receipts / "paper.json").write_text(json.dumps(paper))
    result = review_host_trial(archive_root=archive, receipts_dir=receipts,
                               start_date=BASE)
    assert result["other_receipts_out_of_scope"] == 2
    assert result["invalid_or_unsupported_receipts"] == 0
    assert result["days_with_matching_operator_host_reports"] == 0


def test_early_observation_does_not_attest_later_run(tmp_path):
    archive = tmp_path / "archive"
    receipts = tmp_path / "receipts"
    receipts.mkdir()
    path = make_day(archive, BASE)
    make_attestation(receipts, path, name="early.json",
                     stamp=datetime(2026, 10, 1, 5, 29, tzinfo=timezone.utc))
    result = review_host_trial(archive_root=archive, receipts_dir=receipts,
                               start_date=BASE)
    assert result["days_with_matching_operator_host_reports"] == 0


def test_cli_is_read_only_and_private(tmp_path, monkeypatch, capsys):
    archive = tmp_path / "archive"
    receipts = tmp_path / "receipts"
    receipts.mkdir()
    path = make_day(archive, BASE)
    make_attestation(receipts, path, name="one.json")
    before = path.read_bytes()
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(tmp_path / "none.json"))
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(tmp_path / "none-profile.json"))
    import subprocess
    monkeypatch.setattr(subprocess, "run", lambda *_a, **_kw: pytest.fail("No subprocess"))
    assert main([
        "host-trial-review", "--archive-root", str(archive),
        "--receipts-dir", str(receipts),
        "--start-date", str(BASE),
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["days_with_matching_operator_host_reports"] == 1
    assert "secret-case-888" not in json.dumps(result)
    assert path.read_bytes() == before


@pytest.mark.parametrize("days", [0, 4, 15, True])
def test_refuse_invalid_windows(tmp_path, days):
    a, r = tmp_path / "archive", tmp_path / "receipts"
    a.mkdir()
    r.mkdir()
    with pytest.raises(HostTrialReviewError, match="trial_days"):
        review_host_trial(archive_root=a, receipts_dir=r, start_date=BASE, days=days)
