"""Privacy and consent regression tests for the local incident schema (#20)."""
from __future__ import annotations

from datetime import date
import json
import os

import pytest

from kushluk import incident
from kushluk.cli import main
from kushluk.config import Settings
from kushluk.operations import OperationError, operate_request


DAY = date(2026, 10, 17)


def settings(tmp_path):
    return Settings(archive_dir=tmp_path / "archive", output_dir=tmp_path / "output")


def fake_run_report(*, status="needs_review", code="manual_review_no_auto_retry",
                    failures=None, print_state="submission_uncertain",
                    archived=True):
    return {
        "status": status,
        "failure_codes": failures or [],
        "delivery": {"print": print_state, "email": "not_requested",
                     "physical_print_verified": False},
        "timing": {"validated_archived": archived},
        "operator_guidance": {"code": code,
                              "message": "UNTRUSTED_RAW_REPORT_PRIVATE_PASSWORD"},
    }


@pytest.mark.parametrize("code,expected_component,expected_severity", [
    ("manual_review_no_auto_retry", "scheduler", "failed"),
    ("delivery_needs_attention", "delivery", "failed"),
    ("archive_ready_late", "scheduler", "degraded"),
    ("no_run_receipt", "scheduler", "degraded"),
    ("schedule_paused", "scheduler", "info"),
    ("run_in_progress", "scheduler", "info"),
    ("printer_queue_not_physical_proof", "printer", "info"),
    ("smtp_accepted_not_recipient_proof", "email", "info"),
    ("archive_complete_delivery_not_implied", "archive", "info"),
    ("status_requires_review", "scheduler", "failed"),
])
def test_bounded_known_incident_categories(tmp_path, monkeypatch, code,
                                           expected_component, expected_severity):
    state = {
        "manual_review_no_auto_retry": "needs_review",
        "delivery_needs_attention": "completed",
        "no_run_receipt": "not_run",
        "schedule_paused": "paused",
        "run_in_progress": "in_progress",
    }.get(code, "completed")
    monkeypatch.setattr(incident, "run_report", lambda *a, **k: fake_run_report(
        status=state, code=code,
    ))
    event = incident.build_incident_report(settings(tmp_path), target_date=DAY)
    assert event["component"] == expected_component
    assert event["severity"] == expected_severity
    assert event["human_notice"]["code"] == code
    assert event["remote_report_sent"] is False
    assert event["remote_report_authorized"] is False
    assert event["delivery_attempted_by_report"] is False
    assert event["suggested_actions"][0]["automatic_retry_allowed"] is False
    assert "UNTRUSTED_RAW_REPORT" not in json.dumps(event)


def test_sanitizes_injected_secret_failure_and_delivery(tmp_path, monkeypatch):
    secret = "https://private.example.test/ics?token=SHOULD_NEVER_LEAK"
    monkeypatch.setattr(incident, "run_report", lambda *a, **k: fake_run_report(
        failures=["print_failed", secret, "api_key_top_secret", ["broken"]],
        print_state=secret,
    ))
    event = incident.build_incident_report(settings(tmp_path), target_date=DAY)
    flat = json.dumps(event)
    assert "print_failed" in flat
    assert "unclassified_failure" in flat
    assert secret not in flat
    assert "api_key_top_secret" not in flat
    assert "SHOULD_NEVER_LEAK" not in flat
    assert event["delivery"]["printer_submission"] == "unknown"
    assert event["delivery"]["paper_verified"] is False
    assert event["edition_usable"] == "validated_archive_reported"


def test_repeat_read_never_changes_archive_and_incident_id_stable(tmp_path):
    cfg = settings(tmp_path)
    before = incident.build_incident_report(cfg, target_date=DAY)
    after = incident.build_incident_report(cfg, target_date=DAY)
    assert before["incident_id"] == after["incident_id"]
    assert before["status"] == "not_run"
    assert before["user_notification_required"] is False
    assert before["edition_usable"] == "not_established"
    assert not cfg.archive_dir.exists()


def test_local_cli_and_agent_action_never_contacts_sinks(tmp_path, monkeypatch, capsys):
    cfg = settings(tmp_path)
    monkeypatch.setenv("KUSHLUK_ARCHIVE_DIR", str(cfg.archive_dir))
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(tmp_path / "missing-profile.json"))
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(tmp_path / "missing-sources.json"))
    monkeypatch.setattr("kushluk.printing.print_pdf",
                        lambda *a, **k: pytest.fail("Never print"))
    assert main(["incident-report", "--date", str(DAY)]) == 0
    event = json.loads(capsys.readouterr().out)
    assert event["kind"] == "local_run_incident"
    assert event["remote_report_sent"] is False
    agent = operate_request(cfg, {
        "schema_version": 1, "action": "incident_report", "date": str(DAY),
    })
    assert agent["status"] == "not_run"
    assert agent["outcome"]["incident_id"] == event["incident_id"]
    assert agent["remote_report_sent"] is False
    assert not cfg.archive_dir.exists()
    with pytest.raises(OperationError, match="unknown_fields"):
        operate_request(cfg, {
            "schema_version": 1, "action": "incident_report", "date": str(DAY),
            "recipient": "https://telemetry.example.test/",
        })


def test_private_export_is_mode_0600_and_create_only(tmp_path, monkeypatch, capsys):
    cfg = settings(tmp_path)
    monkeypatch.setenv("KUSHLUK_ARCHIVE_DIR", str(cfg.archive_dir))
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(tmp_path / "missing-profile.json"))
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(tmp_path / "missing-sources.json"))
    file = tmp_path / "review" / "incident.json"
    argv = ["incident-report", "--date", str(DAY), "--output", str(file)]
    assert main(argv) == 0
    response = json.loads(capsys.readouterr().out)
    assert response["status"] == "private_incident_report_written"
    assert response["remote_report_sent"] is False
    assert json.loads(file.read_text())["report_prepared"] is True
    if os.name != "nt":
        assert file.stat().st_mode & 0o777 == 0o600
    old = file.read_bytes()
    assert main(argv) == 2
    assert json.loads(capsys.readouterr().out)["error"] == "incident_export_failed"
    assert file.read_bytes() == old
    assert not cfg.archive_dir.exists()


def test_existing_symlink_cannot_be_overwritten_or_followed(tmp_path):
    cfg = settings(tmp_path)
    original = tmp_path / "private-content.json"
    original.write_text("private original stays intact")
    link = tmp_path / "destination.json"
    link.symlink_to(original)
    with pytest.raises(ValueError, match="already_exists"):
        incident.save_private_incident_report(
            link, incident.build_incident_report(cfg, target_date=DAY),
        )
    assert original.read_text() == "private original stays intact"


def test_real_malformed_receipt_only_returns_fixed_failure_codes(tmp_path):
    cfg = settings(tmp_path)
    folder = cfg.archive_dir / "20261017-001"
    folder.mkdir(parents=True)
    payload = {
        "schema_version": 1, "edition_id": "20261017-001",
        "status": "needs_review", "stage": "interrupted",
        "failure_codes": ["print_failed", "token_PRIVATE_PASSWORD"],
        "request": {"send_to_printer": True},
    }
    (folder / "scheduled.json").write_text(json.dumps(payload))
    report = incident.build_incident_report(cfg, target_date=DAY)
    assert report["status"] == "needs_review"
    assert "print_failed" in report["failure_codes"]
    assert "token_PRIVATE_PASSWORD" not in json.dumps(report)
    assert "unclassified_failure" in report["failure_codes"]
    assert report["user_notification_required"] is True


def test_export_refuses_symlinked_or_public_parent(tmp_path):
    cfg = settings(tmp_path)
    report = incident.build_incident_report(cfg, target_date=DAY)
    private = tmp_path / "private"
    private.mkdir(mode=0o700)
    shortcut = tmp_path / "shortcut"
    shortcut.symlink_to(private, target_is_directory=True)
    with pytest.raises(ValueError, match="unsafe_directory"):
        incident.save_private_incident_report(shortcut / "incident.json", report)
    assert not (private / "incident.json").exists()
    private.chmod(0o755)
    with pytest.raises(ValueError, match="unsafe_directory"):
        incident.save_private_incident_report(private / "incident.json", report)
    assert not (private / "incident.json").exists()
