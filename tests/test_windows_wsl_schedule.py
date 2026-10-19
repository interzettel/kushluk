"""Review-only Windows Task Scheduler exporter for WSL2, including hostile input."""
import json
from pathlib import Path
import stat

import pytest

from kushluk.cli import main
from kushluk.schedule_templates import (
    ScheduleTemplateError, export_templates, templates,
)


def options(tmp_path):
    return dict(
        platform="windows-wsl",
        executable=Path("/home/reader/kushluk/.venv/bin/kushluk"),
        working_dir=Path("/home/reader/kushluk"),
        output_dir=tmp_path / "review",
        start="07:30",
        latest_start="07:45",
        ready_by="08:00",
        wsl_distro="Ubuntu-24.04",
    )


def test_review_first_windows_template_has_real_wsl_boundary(tmp_path):
    config = options(tmp_path)
    files = export_templates(**config)
    assert files == ["kushluk-windows-wsl.ps1"]
    path = config["output_dir"] / files[0]
    script = path.read_text(encoding="utf-8")
    assert "param([switch]$Register)" in script
    assert "if (-not $Register)" in script
    assert "New-ScheduledTaskTrigger -Daily" in script
    assert "New-ScheduledTaskPrincipal" in script
    assert "-LogonType Interactive -RunLevel Limited" in script
    assert "Get-ScheduledTask -TaskName $taskName" in script
    assert 'Ubuntu-24.04 -- bash -lc' in script
    assert (
        "exec /home/reader/kushluk/.venv/bin/kushluk run "
        "--expected-start 07:30 --latest-start 07:45 --ready-by 08:00"
    ) in script
    assert "-NoProfile" not in script
    assert all(x not in script for x in [
        "--print", "--email", "Start-Process", "Invoke-Expression",
        "-WakeToRun", "Register-ScheduledTask -Force",
    ])
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert stat.S_IMODE(config["output_dir"].stat().st_mode) == 0o700
    with pytest.raises(ScheduleTemplateError, match="schedule_files_exist"):
        export_templates(**config)


@pytest.mark.parametrize("updates,error", [
    ({"wsl_distro": "Ubuntu-24.04;whoami"}, "invalid_wsl_distro"),
    ({"wsl_distro": ""}, "invalid_wsl_distro"),
    ({"wsl_distro": "Ubuntu \'something"}, "invalid_wsl_distro"),
    ({"executable": Path("/bin/kushluk;evil")}, "absolute_executable_path_required"),
    ({"working_dir": Path("/home/reader/kushluk space")},
     "systemd_workdir_contains_unsupported_characters"),
    ({"working_dir": Path("/home/reader/kushluk;whoami")},
     "systemd_workdir_contains_unsupported_characters"),
    ({"ready_by": "07:45"}, "cutoff_must_precede_ready_by"),
    ({"ready_by": "00:00"}, "cutoff_must_precede_ready_by"),
    ({"ready_by": "24:00"}, "clock_must_be_HH_MM"),
])
def test_invalid_windows_template_fields_are_rejected(tmp_path, updates, error):
    config = options(tmp_path)
    config.update(updates)
    with pytest.raises(ScheduleTemplateError, match=error):
        export_templates(**config)
    assert not config["output_dir"].exists()


def test_cli_creates_only_review_file_without_running_host_actions(tmp_path, monkeypatch, capsys):
    import subprocess
    monkeypatch.setenv("KUSHLUK_PROFILE_FILE", str(tmp_path / "missing-profile.json"))
    monkeypatch.setenv("KUSHLUK_SOURCE_REGISTRY", str(tmp_path / "missing-sources.json"))
    monkeypatch.setattr(subprocess, "run", lambda *_a, **_kw:
                        pytest.fail("Must not call OS scheduler or printer"))
    args = [
        "schedule-export", "--platform", "windows-wsl",
        "--executable", "/home/reader/kushluk/.venv/bin/kushluk",
        "--working-dir", "/home/reader/kushluk",
        "--output-dir", str(tmp_path / "review"),
        "--wsl-distro", "Ubuntu-24.04",
        "--start", "07:20", "--latest-start", "07:50",
        "--ready-by", "08:00",
    ]
    assert main(args) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "templates_created_not_installed"
    assert output["schedule_enabled"] is False
    assert output["printing_enabled"] is False
    assert output["host_verified"] is False
    script = templates(
        platform="windows-wsl",
        executable=Path("/home/reader/kushluk/.venv/bin/kushluk"),
        working_dir=Path("/home/reader/kushluk"),
        start="07:20", latest_start="07:50",
        ready_by="08:00",
    )["kushluk-windows-wsl.ps1"]
    assert "--expected-start 07:20 --latest-start 07:50 --ready-by 08:00" in script
