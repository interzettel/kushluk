"""Contract tests for local operations and non-duplicating scheduled controls."""
from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from kushluk import operations, scheduled
from kushluk.config import Settings
from kushluk.operations import OperationError, operate_file, operate_request


DAY = date(2026, 9, 23)


def settings(tmp_path):
    return Settings(
        archive_dir=tmp_path / "archive", output_dir=tmp_path / "output",
        timezone="Europe/Berlin",
    )


def fixture_result():
    return SimpleNamespace(failures=[], print_result=None, email_result=None,
                           pdf_path=Path("synthetic-already-validated.pdf"))


def request(action, **kwargs):
    return {"schema_version": 1, "action": action, "date": DAY.isoformat(), **kwargs}


def moment(hour, minute=0):
    return datetime(2026, 9, 23, hour, minute, tzinfo=timezone.utc)


def test_pause_is_private_and_blocks_run_without_archive_or_delivery(tmp_path, monkeypatch):
    cfg = settings(tmp_path)
    calls = []
    monkeypatch.setattr(scheduled, "run_pipeline", lambda *_a, **_kw: calls.append(1))
    before = operate_request(cfg, request("status"))
    assert before["status"] == "not_run"
    first = operate_request(cfg, request("pause"))
    assert first["status"] == "paused"
    marker = cfg.archive_dir / "20260923-001" / ".kushluk-paused.json"
    assert marker.stat().st_mode & 0o777 == 0o600
    assert operate_request(cfg, request("pause"))["status"] == "already_paused"
    assert operate_request(cfg, request("status"))["status"] == "paused"
    attempted = operate_request(cfg, request(
        "run", print=True, acknowledge_delivery=True,
    ), now=moment(5))
    assert attempted["status"] == "paused"
    assert calls == []
    assert not (marker.parent / "scheduled.json").exists()
    assert operate_request(cfg, request("resume"))["status"] == "resumed"
    assert operate_request(cfg, request("resume"))["status"] == "not_paused"
    assert not calls


def test_resume_does_not_erase_unknown_marker_or_symlink(tmp_path):
    cfg = settings(tmp_path)
    marker = cfg.archive_dir / "20260923-001" / ".kushluk-paused.json"
    marker.parent.mkdir(parents=True)
    marker.write_text('{"schema_version": 666, "paused": true}', encoding="utf-8")
    assert operate_request(cfg, request("resume"))["status"] == "needs_review"
    assert marker.exists()
    assert scheduled.run_once(cfg, target_date=DAY).status == "needs_review"
    marker.unlink()
    private = tmp_path / "private-file.json"
    private.write_text("private")
    marker.symlink_to(private)
    assert operate_request(cfg, request("resume"))["status"] == "needs_review"
    assert marker.is_symlink()
    assert private.read_text() == "private"


def test_last_start_is_local_time_and_never_creates_a_run_receipt(tmp_path, monkeypatch):
    cfg = settings(tmp_path)
    calls = []
    monkeypatch.setattr(scheduled, "run_pipeline", lambda *_a, **_kw: calls.append(1))
    # September in Berlin is UTC+2, so 06:01 UTC is 08:01 local.
    late = operate_request(cfg, request("run", latest_start="08:00"), now=moment(6, 1))
    assert late["status"] == "deadline_missed"
    assert late["outcome"]["failure_codes"] == ["latest_start_missed"]
    assert calls == []
    assert not (cfg.archive_dir / "20260923-001" / "scheduled.json").exists()


def test_start_cutoff_allows_one_run_but_replays_never_regenerate(tmp_path, monkeypatch):
    cfg = settings(tmp_path)
    calls = []

    def pipeline(*args, **kwargs):
        calls.append(1)
        return fixture_result()

    monkeypatch.setattr(scheduled, "run_pipeline", pipeline)
    req = request("run", latest_start="08:00")
    one = operate_request(cfg, req, now=moment(5, 30))
    two = operate_request(cfg, req, now=moment(13))
    assert one["status"] == "completed"
    assert two["status"] == "already_completed"
    assert len(calls) == 1
    assert operate_request(cfg, request("status"))["status"] == "completed"
    assert (cfg.archive_dir / "20260923-001" / "scheduled.json").is_file()


def test_pause_during_an_active_run_does_not_claim_the_job_was_cancelled(
    tmp_path, monkeypatch,
):
    cfg = settings(tmp_path)
    observations = []

    def pipeline(*args, **kwargs):
        outcome = scheduled.pause_day(cfg, target_date=DAY)
        observations.append(outcome.status)
        return fixture_result()

    monkeypatch.setattr(scheduled, "run_pipeline", pipeline)
    first = scheduled.run_once(cfg, target_date=DAY)
    assert observations == ["paused"]
    assert first.status == "completed"
    assert scheduled.read_run_status(cfg, target_date=DAY).status == "completed"
    assert scheduled.run_once(cfg, target_date=DAY).status == "already_completed"


def test_print_requires_explicit_permission_and_submits_once_at_most(
    tmp_path, monkeypatch,
):
    cfg = settings(tmp_path)
    sent = []

    def pipeline(*args, **kwargs):
        sent.append("print")
        kwargs["before_delivery"]("print")
        return SimpleNamespace(
            failures=[], print_result=SimpleNamespace(success=True),
            email_result=None, pdf_path=Path("synthetic.pdf"),
        )

    monkeypatch.setattr(scheduled, "run_pipeline", pipeline)
    requested = request("run", print=True)
    with pytest.raises(OperationError, match="delivery_consent_required"):
        operate_request(cfg, requested)
    assert not cfg.archive_dir.exists()
    requested["acknowledge_delivery"] = True
    assert operate_request(cfg, requested)["status"] == "completed"
    assert operate_request(cfg, requested)["status"] == "already_completed"
    assert sent == ["print"]
    assert operate_request(cfg, request("status"))["outcome"]["print_submitted"] is True


def test_reprint_never_happens_without_acknowledgment(tmp_path, monkeypatch):
    cfg = settings(tmp_path)
    deliveries = []

    def fake_archive(*args, **kwargs):
        deliveries.append(kwargs)
        return SimpleNamespace(as_dict=lambda: {
            "schema_version": 1, "status": "submitted", "edition_id": "20260923-001",
        })

    monkeypatch.setattr(operations, "deliver_archived", fake_archive)
    req = request("deliver_archived", channel="print", request_id="owner-01")
    with pytest.raises(OperationError, match="explicit_reprint_consent_required"):
        operate_request(cfg, req)
    assert deliveries == []
    req["acknowledge_possible_duplicate"] = True
    result = operate_request(cfg, req)
    assert result["status"] == "submitted"
    assert len(deliveries) == 1
    assert deliveries[0]["acknowledge_possible_duplicate"] is True
    assert deliveries[0]["request_id"] == "owner-01"


@pytest.mark.parametrize("invalid,error", [
    (request("run", email_on_print_failure=True), "fallback_requires_print"),
    (request("run", print=1), "invalid_boolean"),
    (request("run", print=True), "delivery_consent_required"),
    (request("run", latest_start="8:00"), "invalid_latest_start"),
    (request("run", latest_start="25:30"), "invalid_latest_start"),
    (request("run", print_profile="unsupported"), "invalid_print_profile"),
    (request("run", unknown="some-secret"), "unknown_fields"),
    (request("status", email=True), "unknown_fields"),
    (request("deliver_archived", channel="print", request_id="../x",
             acknowledge_possible_duplicate=True), "invalid_request_id"),
    ({"schema_version": 2, "action": "run", "date": DAY.isoformat()}, "unsupported_schema"),
    ({"schema_version": 1, "action": "run", "date": "yesterday"}, "invalid_date"),
    ({"schema_version": 1, "action": "shell", "date": DAY.isoformat()}, "unsupported_action"),
])
def test_operation_request_validation_is_fail_closed(tmp_path, invalid, error):
    cfg = settings(tmp_path)
    with pytest.raises(OperationError, match=error):
        operate_request(cfg, invalid)
    assert not cfg.archive_dir.exists()


def test_file_boundary_is_small_private_and_not_remote(tmp_path, monkeypatch):
    cfg = settings(tmp_path)
    file = tmp_path / "command.json"
    file.write_text(json.dumps(request("status")))
    assert operate_file(cfg, file)["status"] == "not_run"
    file.write_text("{bad-json")
    with pytest.raises(OperationError, match="invalid_request_file"):
        operate_file(cfg, file)
    file.write_text("x" * 5000)
    with pytest.raises(OperationError, match="invalid_request_file"):
        operate_file(cfg, file)
    file.write_text(json.dumps(request("status")))
    alias = tmp_path / "alias.json"
    alias.symlink_to(file)
    with pytest.raises(OperationError, match="invalid_request_file"):
        operate_file(cfg, alias)


def test_command_line_still_works_without_starting_services(tmp_path, monkeypatch, capsys):
    from kushluk.cli import main
    cfg = settings(tmp_path)
    monkeypatch.setenv("KUSHLUK_ARCHIVE_DIR", str(cfg.archive_dir))
    monkeypatch.setenv("KUSHLUK_OUTPUT_DIR", str(cfg.output_dir))
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(tmp_path / "none.json"))
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(tmp_path / "none-registry.json"))
    assert main(["pause-day", "--date", DAY.isoformat()]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "paused"
    assert main(["run-status", "--date", DAY.isoformat()]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "paused"
    assert main(["resume-day", "--date", DAY.isoformat()]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "resumed"
    file = tmp_path / "op.json"
    file.write_text(json.dumps(request("status")))
    assert main(["operate", "--request", str(file)]) == 0
    assert json.loads(capsys.readouterr().out)["schema_version"] == 1
    file.write_text(json.dumps(request("run", print=True)))
    assert main(["operate", "--request", str(file)]) == 2
    assert json.loads(capsys.readouterr().out)["error"] == "delivery_consent_required"
    assert not (cfg.archive_dir / "20260923-001" / "scheduled.json").exists()
