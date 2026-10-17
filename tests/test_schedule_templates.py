"""Native schedule templates are reversible files, not an installed timer."""
from datetime import time
from pathlib import Path
import plistlib
import stat

import pytest

from kushluk.cli import main
from kushluk.schedule_templates import (
    ScheduleTemplateError, export_templates, templates,
)


def args(tmp_path, platform="systemd"):
    return dict(
        platform=platform,
        executable=Path("/opt/kushluk/.venv/bin/kushluk"),
        working_dir=Path("/home/reader/kushluk"),
        output_dir=tmp_path / "exports",
        start="07:30",
        latest_start="07:45",
    )


def test_systemd_timer_is_daily_user_scoped_and_guarded(tmp_path):
    opts = args(tmp_path)
    names = export_templates(**opts)
    assert names == ["kushluk.service", "kushluk.timer"]
    service = (opts["output_dir"] / "kushluk.service").read_text()
    timer = (opts["output_dir"] / "kushluk.timer").read_text()
    assert "Type=oneshot" in service
    assert "ExecStart=/opt/kushluk/.venv/bin/kushluk run --latest-start 07:45" in service
    assert "UMask=0077" in service
    assert "OnCalendar=*-*-* 07:30:00" in timer
    assert "Persistent=true" in timer
    assert "WantedBy=timers.target" in timer
    assert not any(term in service + timer for term in (
        "curl", "token=", "smtp_", "systemctl enable", "lp -d", "print --",
    ))
    assert all(stat.S_IMODE((opts["output_dir"] / name).stat().st_mode) == 0o600
               for name in names)
    with pytest.raises(ScheduleTemplateError, match="schedule_files_exist"):
        export_templates(**opts)


def test_launchd_plist_is_no_shell_and_no_autostart(tmp_path):
    opts = args(tmp_path, "launchd")
    names = export_templates(**opts)
    payload = plistlib.loads((opts["output_dir"] / names[0]).read_bytes())
    assert payload["ProgramArguments"] == [
        "/opt/kushluk/.venv/bin/kushluk", "run", "--latest-start", "07:45",
    ]
    assert payload["StartCalendarInterval"] == {"Hour": 7, "Minute": 30}
    assert payload["RunAtLoad"] is False
    assert payload["WorkingDirectory"] == "/home/reader/kushluk"
    assert payload["Label"] == "org.interzettel.kushluk.morning"


@pytest.mark.parametrize("change,error", [
    ({"start": "08:00"}, "start_must_precede_latest_start"),
    ({"start": "99:00"}, "clock_must_be_HH_MM"),
    ({"latest_start": "06:00"}, "start_must_precede_latest_start"),
    ({"executable": Path("kushluk")}, "absolute_executable_path_required"),
    ({"executable": Path("/bin/kushluk;touch /tmp/pwned")},
     "absolute_executable_path_required"),
    ({"working_dir": Path("../secret")}, "absolute_workdir_required"),
    ({"working_dir": Path("/home/reader/a b")}, "systemd_workdir_contains"),
    ({"platform": "cloud"}, "unsupported_platform"),
])
def test_bad_or_injectable_config_is_rejected_before_output(tmp_path, change, error):
    opts = args(tmp_path)
    opts.update(change)
    with pytest.raises(ScheduleTemplateError, match=error):
        export_templates(**opts)
    assert not (tmp_path / "exports").exists()


def test_output_symlink_and_create_only_never_overwrite(tmp_path):
    opts = args(tmp_path)
    outside = tmp_path / "private"
    outside.mkdir()
    (outside / "keep").write_text("secret")
    opts["output_dir"].symlink_to(outside, target_is_directory=True)
    with pytest.raises(ScheduleTemplateError, match="absolute_output_dir_required"):
        export_templates(**opts)
    assert (outside / "keep").read_text() == "secret"


def test_cli_exports_without_enabling_anything(tmp_path, monkeypatch, capsys):
    import json
    from kushluk import schedule_templates

    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(tmp_path / "none.json"))
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(tmp_path / "none-sources.json"))

    # If code tried to run systemctl/launchctl/print, this test would fail.
    import subprocess
    monkeypatch.setattr(subprocess, "run", lambda *_a, **_kw: pytest.fail("No execution"))
    cli_args = [
        "schedule-export", "--platform", "launchd",
        "--executable", "/opt/kushluk/.venv/bin/kushluk",
        "--working-dir", str(tmp_path),
        "--output-dir", str(tmp_path / "scheduler"),
        "--start", "07:20", "--latest-start", "07:50",
    ]
    assert main(cli_args) == 0
    response = json.loads(capsys.readouterr().out)
    assert response["status"] == "templates_created_not_installed"
    assert response["schedule_enabled"] is False
    assert response["printing_enabled"] is False
    assert response["host_verified"] is False
    assert schedule_templates.templates(
        platform="launchd", executable=Path("/opt/kushluk/.venv/bin/kushluk"),
        working_dir=tmp_path, start="07:20", latest_start="07:50",
    )
