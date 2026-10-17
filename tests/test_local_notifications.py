"""Opt-in desktop notice never implies a physical or visible notification."""
from __future__ import annotations

from datetime import date
import json
import os
import subprocess

import pytest

from kushluk import local_notifications as notices
from kushluk.cli import main
from kushluk.config import Settings
from kushluk.scheduled import ScheduledOutcome

DAY = date(2026, 10, 17)


def config(tmp_path):
    return Settings(archive_dir=tmp_path / "archive", output_dir=tmp_path / "out")


def fake_incident(needed=True):
    return {
        "schema_version": 1, "kind": "local_run_incident",
        "incident_id": "local-2f18abcd735a", "edition_id": "20261017-001",
        "user_notification_required": needed,
        "severity": "failed" if needed else "info",
        "error_code": "manual_review_no_auto_retry" if needed
        else "archive_complete_delivery_not_implied",
    }


def test_preview_is_read_only_and_non_notifiable_dates_are_quiet(tmp_path, monkeypatch):
    cfg = config(tmp_path)
    monkeypatch.setattr(notices, "build_incident_report", lambda *a, **kw: fake_incident())
    monkeypatch.setattr(notices.subprocess, "run",
                        lambda *_a, **_kw: pytest.fail("Never call native backend"))
    result = notices.notify_local(cfg, target_date=DAY)
    assert result["status"] == "preview_only"
    assert result["notification_sent_to_os"] is False
    assert result["notification_display_verified"] is False
    assert not cfg.archive_dir.exists()
    monkeypatch.setattr(notices, "build_incident_report",
                        lambda *a, **kw: fake_incident(False))
    result = notices.notify_local(cfg, target_date=DAY, send=True, system="Linux")
    assert result["status"] == "not_required"
    assert not cfg.archive_dir.exists()


def test_native_linux_submission_is_explicit_constant_and_at_most_once(
    tmp_path, monkeypatch,
):
    cfg = config(tmp_path)
    folder = cfg.archive_dir / "20261017-001"
    folder.mkdir(parents=True)
    monkeypatch.setattr(notices, "build_incident_report", lambda *a, **kw: fake_incident())
    monkeypatch.setattr(notices.shutil, "which", lambda name: "/usr/bin/notify-send")
    executed = []

    def run(cmd, **kwargs):
        executed.append((cmd, kwargs))
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(notices.subprocess, "run", run)
    first = notices.notify_local(cfg, target_date=DAY, send=True, system="Linux")
    assert first["status"] == "submitted_to_os_not_verified"
    assert first["notification_sent_to_os"] is True
    assert first["notification_display_verified"] is False
    assert len(executed) == 1
    assert executed[0][0][0] == "/usr/bin/notify-send"
    assert executed[0][1]["timeout"] == 5
    assert "shell" not in executed[0][1]
    assert executed[0][0][-1] == "A morning run needs review. Open Kushluk status."
    receipt = folder / ".notification-local-2f18abcd735a.json"
    assert json.loads(receipt.read_text())["os_submission_state"] == (
        "accepted_not_display_verified"
    )
    if os.name != "nt":
        assert receipt.stat().st_mode & 0o777 == 0o600
    again = notices.notify_local(cfg, target_date=DAY, send=True, system="Linux")
    assert again["status"] == "already_submitted"
    assert len(executed) == 1


def test_os_failure_never_auto_retries_uncertain_submission(tmp_path, monkeypatch):
    cfg = config(tmp_path)
    (cfg.archive_dir / "20261017-001").mkdir(parents=True)
    monkeypatch.setattr(notices, "build_incident_report", lambda *a, **kw: fake_incident())
    monkeypatch.setattr(notices.shutil, "which", lambda name: "/usr/bin/notify-send")
    calls = []
    monkeypatch.setattr(notices.subprocess, "run",
                        lambda cmd, **kw: (
                            calls.append(cmd) or subprocess.CompletedProcess(cmd, 3, "", "")
                        ))
    first = notices.notify_local(cfg, target_date=DAY, send=True, system="Linux")
    assert first["status"] == "os_submission_uncertain_no_auto_retry"
    second = notices.notify_local(cfg, target_date=DAY, send=True, system="Linux")
    assert second["status"] == "already_submitted"
    assert len(calls) == 1
    receipt = cfg.archive_dir / "20261017-001" / ".notification-local-2f18abcd735a.json"
    assert json.loads(receipt.read_text())["os_submission_state"] == "uncertain"


def test_unsupported_host_or_no_interactive_executable_stays_local(
    tmp_path, monkeypatch,
):
    cfg = config(tmp_path)
    monkeypatch.setattr(notices, "build_incident_report", lambda *a, **kw: fake_incident())
    monkeypatch.setattr(notices.shutil, "which", lambda name: None)
    assert notices.notify_local(cfg, target_date=DAY, send=True, system="Windows")[
        "status"
    ] == "os_backend_unavailable"
    assert notices.notify_local(cfg, target_date=DAY, send=True, system="Linux")[
        "status"
    ] == "os_backend_unavailable"
    assert not cfg.archive_dir.exists()


def test_private_data_cannot_be_injected_into_macos_osascript(
    tmp_path, monkeypatch,
):
    cfg = config(tmp_path)
    (cfg.archive_dir / "20261017-001").mkdir(parents=True)
    monkeypatch.setattr(notices, "build_incident_report", lambda *a, **kw: {
        **fake_incident(), "error_code": '"; do shell script "curl private.example"',
        "human_notice": {"message": "SECRET_CALENDAR_TOKEN"},
    })
    monkeypatch.setattr(notices.shutil, "which", lambda name: "/usr/bin/osascript")
    commands = []

    def fake_run(cmd, **kwargs):
        commands.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(notices.subprocess, "run", fake_run)
    result = notices.notify_local(cfg, target_date=DAY, send=True, system="Darwin")
    assert result["status"] == "submitted_to_os_not_verified"
    assert len(commands) == 1
    assert "SECRET_CALENDAR_TOKEN" not in repr(commands)
    assert "curl" not in repr(commands)
    assert commands[0] == [
        "/usr/bin/osascript", "-e",
        'display notification "A morning run needs review. Open Kushluk status." '
        'with title "Kushluk"',
    ]


def test_rejects_symlink_archive_and_unsafe_notification_lock(
    tmp_path, monkeypatch,
):
    cfg = config(tmp_path)
    real = tmp_path / "real"
    real.mkdir()
    cfg.archive_dir.symlink_to(real, target_is_directory=True)
    (real / "20261017-001").mkdir()
    monkeypatch.setattr(notices, "build_incident_report", lambda *a, **kw: fake_incident())
    monkeypatch.setattr(notices.shutil, "which", lambda name: "/usr/bin/notify-send")
    monkeypatch.setattr(notices.subprocess, "run",
                        lambda *_a, **_kw: pytest.fail("No send via symlink"))
    assert notices.notify_local(cfg, target_date=DAY, send=True, system="Linux")[
        "status"
    ] == "unsafe_or_missing_archive"


def test_cli_preview_and_explicit_run_opt_in(tmp_path, monkeypatch, capsys):
    cfg = config(tmp_path)
    monkeypatch.setenv("KUSHLUK_ARCHIVE_DIR", str(cfg.archive_dir))
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(tmp_path / "no-profile"))
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(tmp_path / "no-sources"))
    assert main(["notify-local", "--date", str(DAY)]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "not_required"
    calls = []
    monkeypatch.setattr("kushluk.cli.run_once",
                        lambda *_a, **_kw: ScheduledOutcome("needs_review", "20261017-001"))
    monkeypatch.setattr("kushluk.cli.notify_local",
                        lambda *_a, **kw: (
                            calls.append(kw) or {"status": "submitted_to_os_not_verified"}
                        ))
    assert main(["run", "--date", str(DAY)]) == 2
    assert calls == []
    assert main(["run", "--date", str(DAY), "--notify-local"]) == 2
    result = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert result["local_notification"]["status"] == "submitted_to_os_not_verified"
    assert calls == [{"target_date": DAY, "send": True}]
