"""Privacy-safe readiness diagnostics and history-driven schedule planning."""
from __future__ import annotations

from datetime import date, datetime, timedelta, time, timezone
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from kushluk import scheduled
from kushluk.cli import main
from kushluk.config import Settings
from kushluk.operations import OperationError, operate_request
from kushluk.run_metrics import run_report, timing_plan


TARGET = date(2026, 9, 23)


def cfg(tmp_path):
    return Settings(
        archive_dir=tmp_path / "archive", output_dir=tmp_path / "out",
        timezone="Europe/Berlin",
    )


def record_day(settings, day, *, seconds=180, status="completed", secret=None,
               expected_start=None):
    """Controlled, purely synthetic timestamped local receipt, never live hardware."""
    folder = settings.archive_dir / f"{day:%Y%m%d}-001"
    folder.mkdir(parents=True, exist_ok=True)
    start = datetime.combine(day, time(5, 45), tzinfo=timezone.utc)
    def stamp(diff):
        return (start + timedelta(seconds=diff)).isoformat()
    events = [
        {"stage": "started", "at": stamp(0)},
        {"stage": "sources_complete", "at": stamp(20)},
        {"stage": "editorial_complete", "at": stamp(30)},
        {"stage": "rendering", "at": stamp(40)},
        {"stage": "rendered", "at": stamp(50)},
        {"stage": "validated", "at": stamp(60)},
        {"stage": "archive_ready", "at": stamp(seconds)},
        {"stage": "complete", "at": stamp(seconds + 2)},
    ]
    if secret:
        events[3]["stage"] = secret
    payload = {
        "schema_version": 1,
        "edition_id": folder.name,
        "status": status,
        "stage": "complete",
        "started_at": stamp(0),
        "finished_at": stamp(seconds + 2),
        "stage_events": events,
        "stages": [row["stage"] for row in events],
        "failure_codes": [],
        "ready_by_local": "08:00",
        "expected_start_local": expected_start,
        "request": {
            "send_to_printer": False, "send_email": False,
            "email_on_print_failure": False, "print_profile": "a4-home",
        },
    }
    (folder / "scheduled.json").write_text(json.dumps(payload), encoding="utf-8")


def test_read_report_measures_archive_readiness_not_printed_output(tmp_path):
    settings = cfg(tmp_path)
    record_day(settings, TARGET, seconds=300)
    report = run_report(settings, target_date=TARGET)
    assert report["status"] == "completed"
    assert report["timing"]["elapsed_to_archive_seconds"] == 300
    assert report["timing"]["ready_by_local"] == "08:00"
    assert report["timing"]["ready_by_met"] is True
    assert report["timing"]["validated_archived"] is True
    assert report["delivery"]["print"] == "not_requested"
    assert report["delivery"]["email"] == "not_requested"
    assert not report["delivery"]["physical_print_verified"]
    assert not report["delivery"]["recipient_delivery_verified"]
    assert report["evidence_scope"] == "local_software_receipt_only"


def test_crashed_and_submission_uncertain_runs_never_claim_readiness(tmp_path):
    settings = cfg(tmp_path)
    record_day(settings, TARGET, seconds=300, status="print_submission_unknown")
    path = settings.archive_dir / "20260923-001" / "scheduled.json"
    payload = json.loads(path.read_text())
    payload["stage"] = "print_submission_unknown"
    payload["stage_events"].append({
        "stage": "print_submission_unknown", "at": payload["finished_at"],
    })
    payload["stages"].append("print_submission_unknown")
    payload["request"]["send_to_printer"] = True
    path.write_text(json.dumps(payload))
    report = run_report(settings, target_date=TARGET)
    assert report["status"] == "needs_review"
    assert report["delivery"]["print"] == "submission_uncertain"
    assert report["delivery"]["physical_print_verified"] is False
    assert report["timing"]["validated_archived"] is True


def test_tampered_events_and_private_urls_never_echo(tmp_path):
    settings = cfg(tmp_path)
    secret = "https://private.example.test/ics?token=PRIVATE-SECRET-123"
    record_day(settings, TARGET, seconds=300, secret=secret)
    report = run_report(settings, target_date=TARGET)
    assert secret not in json.dumps(report)
    assert report["stage_events"] == []
    assert report["timing"]["validated_archived"] is False
    assert report["timing"]["elapsed_to_archive_seconds"] is None


def test_unvalidated_archive_cannot_count_as_timing_sample(tmp_path):
    settings = cfg(tmp_path)
    record_day(settings, TARGET, seconds=300)
    receipt = settings.archive_dir / "20260923-001" / "scheduled.json"
    data = json.loads(receipt.read_text())
    data["stage_events"] = [
        row for row in data["stage_events"] if row["stage"] != "validated"
    ]
    receipt.write_text(json.dumps(data))
    report = run_report(settings, target_date=TARGET)
    assert report["timing"]["validated_archived"] is False


def test_p90_plan_from_previous_synthetic_receipts_is_not_installed(tmp_path):
    settings = cfg(tmp_path)
    day = date(2026, 9, 30)
    for offset, seconds in enumerate((180, 300, 480), start=1):
        record_day(settings, day - timedelta(days=offset), seconds=seconds)
    plan = timing_plan(
        settings, target_date=day, ready_by=time(8), margin_minutes=10,
        history_days=10,
    )
    assert plan["status"] == "suggested_not_installed"
    assert plan["sample_count"] == 3
    assert plan["p90_seconds"] == 480
    assert plan["recommended_start_local"] == "07:42"
    assert plan["recommended_latest_start_local"] == "07:50"
    assert plan["schedule_enabled"] is False
    assert plan["evidence_scope"] == "local_receipts_not_independent_host_proof"
    assert not (settings.archive_dir / "20260930-001").exists()


def test_undersampled_timing_never_claims_adaptive_readiness(tmp_path):
    settings = cfg(tmp_path)
    target = date(2026, 9, 30)
    for offset in (1, 2):
        record_day(settings, target - timedelta(days=offset), seconds=200)
    plan = timing_plan(settings, target_date=target)
    assert plan["status"] == "insufficient_history"
    assert plan["sample_count"] == 2
    assert plan["recommended_start_local"] is None


def test_a_failed_edition_is_not_a_successful_training_sample(tmp_path):
    settings = cfg(tmp_path)
    target = date(2026, 9, 30)
    record_day(settings, target - timedelta(days=1), seconds=200)
    record_day(settings, target - timedelta(days=2), seconds=100, status="needs_review")
    record_day(settings, target - timedelta(days=3), seconds=200, secret="secret!")
    plan = timing_plan(settings, target_date=target)
    assert plan["sample_count"] == 1
    assert plan["status"] == "insufficient_history"


def test_timing_options_are_bounded_and_cannot_enable_a_schedule(tmp_path):
    settings = cfg(tmp_path)
    with pytest.raises(ValueError, match="invalid_timing_options"):
        timing_plan(settings, target_date=TARGET, history_days=400)
    with pytest.raises(ValueError, match="invalid_timing_options"):
        timing_plan(settings, target_date=TARGET, margin_minutes=-1)
    payload = {"schema_version": 1, "action": "timing_plan", "date": str(TARGET)}
    assert operate_request(settings, payload)["status"] == "insufficient_history"
    for bad in ({"margin_minutes": True}, {"history_days": 500}):
        with pytest.raises(OperationError, match="invalid_timing_options"):
            operate_request(settings, {**payload, **bad})
    assert not settings.archive_dir.exists()


def test_real_scheduled_runner_persists_content_free_stage_times(tmp_path, monkeypatch):
    settings = cfg(tmp_path)
    private_secret = "PRIVATE-RSS-TOKEN"

    def fake_run(*_args, **kwargs):
        for stage in ("sources_complete", "editorial_complete", "rendering",
                      "rendered", "validated", "archive_ready", "complete"):
            kwargs["on_stage"](stage)
        return SimpleNamespace(
            failures=[], print_result=None, email_result=None, pdf_path=Path("fixture.pdf")
        )

    monkeypatch.setattr(scheduled, "run_pipeline", fake_run)
    out = scheduled.run_once(
        settings, target_date=TARGET, ready_by=time(8),
    )
    assert out.status == "completed"
    receipt = json.loads(
        (settings.archive_dir / "20260923-001" / "scheduled.json").read_text()
    )
    assert len(receipt["stage_events"]) == 8
    assert receipt["ready_by_local"] == "08:00"
    assert receipt["timezone"] == "Europe/Berlin"
    assert receipt["finished_at"]
    assert private_secret not in json.dumps(receipt)
    assert run_report(settings, target_date=TARGET)["timing"]["validated_archived"] is True


def test_versioned_report_and_plan_are_read_only(tmp_path):
    settings = cfg(tmp_path)
    report = operate_request(settings, {"schema_version": 1, "action": "report",
                                        "date": str(TARGET)})
    assert report["action"] == "report"
    assert report["status"] == "not_run"
    assert not report["physical_verified"]
    plan = operate_request(settings, {"schema_version": 1, "action": "timing_plan",
                                      "date": str(TARGET)})
    assert plan["status"] == "insufficient_history"
    assert not settings.archive_dir.exists()


def test_read_only_cli_operations_do_not_schedule_or_print(tmp_path, monkeypatch, capsys):
    settings = cfg(tmp_path)
    monkeypatch.setenv("KUSHLUK_ARCHIVE_DIR", str(settings.archive_dir))
    monkeypatch.setenv("KUSHLUK_OUTPUT_DIR", str(settings.output_dir))
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(tmp_path / "missing-profile"))
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(tmp_path / "missing-registry"))
    assert main(["run-report", "--date", str(TARGET)]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "not_run"
    assert main(["timing-plan", "--date", str(TARGET)]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "insufficient_history"
    assert not settings.archive_dir.exists()


def test_trigger_to_archive_is_measured_separately_from_process_duration(tmp_path):
    settings = cfg(tmp_path)
    # Expected trigger 07:40 local is 05:40 UTC; process actually starts at 05:45 UTC.
    record_day(settings, TARGET, seconds=300, expected_start="07:40")
    report = run_report(settings, target_date=TARGET)
    assert report["timing"]["expected_trigger_local"] == "07:40"
    assert report["timing"]["trigger_delay_seconds"] == 300
    assert report["timing"]["trigger_to_archive_seconds"] == 600
    assert report["timing"]["elapsed_to_archive_seconds"] == 300


def test_planning_prefers_trigger_to_archive_when_three_samples_exist(tmp_path):
    settings = cfg(tmp_path)
    target = date(2026, 9, 30)
    for offset, seconds in enumerate((180, 300, 480), start=1):
        record_day(settings, target - timedelta(days=offset),
                   seconds=seconds, expected_start="07:40")
    plan = timing_plan(settings, target_date=target)
    assert plan["status"] == "suggested_not_installed"
    assert plan["sample_basis"] == "expected_trigger_to_archive"
    assert plan["trigger_sample_count"] == 3
    assert plan["p90_seconds"] == 780
    assert plan["recommended_start_local"] == "07:37"


def test_run_records_expected_trigger_as_a_clock_not_a_provider_url(
    tmp_path, monkeypatch,
):
    settings = cfg(tmp_path)
    def fake_run(*_args, **kwargs):
        for stage in ("validated", "archive_ready", "complete"):
            kwargs["on_stage"](stage)
        return SimpleNamespace(
            failures=[], print_result=None, email_result=None,
            pdf_path=Path("fixture.pdf"),
        )
    monkeypatch.setattr(scheduled, "run_pipeline", fake_run)
    assert scheduled.run_once(
        settings, target_date=TARGET, ready_by=time(8), expected_start=time(7, 30),
    ).status == "completed"
    receipt = json.loads(
        (settings.archive_dir / "20260923-001" / "scheduled.json").read_text()
    )
    assert receipt["expected_start_local"] == "07:30"
    assert run_report(settings, target_date=TARGET)["timing"]["expected_trigger_local"] == "07:30"


def test_operator_guidance_never_implies_physical_delivery(tmp_path):
    settings = cfg(tmp_path)
    record_day(settings, TARGET)
    record_file = settings.archive_dir / "20260923-001" / "scheduled.json"
    payload = json.loads(record_file.read_text())
    payload["print_submitted"] = True
    payload["request"]["send_to_printer"] = True
    record_file.write_text(json.dumps(payload))
    report = run_report(settings, target_date=TARGET)
    assert report["operator_guidance"]["code"] == "printer_queue_not_physical_proof"
    assert "Verify paper" in report["operator_guidance"]["message"]
    assert report["delivery"]["physical_print_verified"] is False


def test_operator_guidance_for_interrupted_delivery_blocks_silent_retry(tmp_path):
    settings = cfg(tmp_path)
    record_day(settings, TARGET, status="print_submission_unknown")
    path = settings.archive_dir / "20260923-001" / "scheduled.json"
    data = json.loads(path.read_text())
    data["request"]["send_to_printer"] = True
    path.write_text(json.dumps(data))
    report = run_report(settings, target_date=TARGET)
    assert report["operator_guidance"]["code"] == "manual_review_no_auto_retry"
    assert "never start a silent replay" in report["operator_guidance"]["message"]
    assert not report["delivery"]["physical_print_verified"]


def test_operator_guidance_does_not_echo_corrupt_secret(tmp_path):
    settings = cfg(tmp_path)
    record_day(settings, TARGET, secret="token=HIDDEN_SECRET_123")
    report = run_report(settings, target_date=TARGET)
    assert "HIDDEN_SECRET_123" not in json.dumps(report)
    assert report["operator_guidance"]["code"] == "archive_complete_delivery_not_implied"


def test_operator_guidance_without_receipt_is_actionable_and_read_only(tmp_path):
    settings = cfg(tmp_path)
    result = run_report(settings, target_date=TARGET)
    assert result["operator_guidance"]["code"] == "no_run_receipt"
    assert not settings.archive_dir.exists()
