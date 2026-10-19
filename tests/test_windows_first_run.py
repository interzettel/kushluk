"""Windows helper is safe by default; no host access in CI."""
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "windows_first_run.ps1"


def test_first_run_helper_is_readonly_by_default():
    src = SCRIPT.read_text(encoding="utf-8")
    assert "[CmdletBinding(DefaultParameterSetName='Check')]" in src
    assert "[switch]$Install" in src
    assert "[switch]$LaunchSetup" in src
    assert "if ($Install)" in src
    assert "if ($LaunchSetup)" in src
    assert "Read-only diagnosis" in src
    assert "KUSHLUK_PRESENT" in src
    assert "KUSHLUK_MISSING" in src
    assert "wsl" in src
    assert "docker-desktop" in src
    assert "test -x" in src


def test_installer_cannot_overwrite_existing_checkout_or_enable_delivery():
    src = SCRIPT.read_text(encoding="utf-8")
    assert 'if [ -e "$HOME/kushluk" ]' in src
    assert "setup-web --no-open" in src
    assert "python3 -m venv .venv" in src
    for forbidden in (
        "Register-ScheduledTask", "Unregister-ScheduledTask",
        "--print", "--email", "curl | sh", "Invoke-Expression",
        "Start-Process", "sudo rm -rf", "-WakeToRun",
    ):
        assert forbidden not in src
