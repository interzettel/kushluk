"""Static fail-closed contract checks for the optional Windows print bridge.

No PowerShell or physical device is ever invoked by this test module.
"""
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "windows_print_handoff.ps1"


def test_default_is_read_only_and_print_submission_is_explicit():
    src = SCRIPT.read_text(encoding="utf-8")
    for expected in (
        "[CmdletBinding()]",
        "[switch]$Submit",
        "if (-not $Submit)",
        "[switch]$AcknowledgePossibleDuplicate",
        "if (-not $AcknowledgePossibleDuplicate)",
        "Get-FileHash -LiteralPath $PdfPath -Algorithm SHA256",
        "Get-Printer",
        "$_.Name -ceq $PrinterName",
        "PrinterStatus.ToString() -ne 'Normal'",
        "[IO.FileMode]::CreateNew",
        "submission_outcome_uncertain",
        "physical_print_verified = $false",
        "simplex,portrait,paper=A4,noscale,ignore-pdf-print-settings",
        "& $SumatraExe '-print-to' $PrinterName",
    ):
        assert expected in src
    assert src.index("if (-not $Submit)") < src.index("& $SumatraExe")
    assert src.index("[IO.FileMode]::CreateNew") < src.index("& $SumatraExe")


def test_windows_handoff_does_not_schedule_or_silently_retry():
    src = SCRIPT.read_text(encoding="utf-8")
    for forbidden in (
        "Register-ScheduledTask",
        "Invoke-Expression",
        "Start-Process",
        "-print-to-default",
        "-WakeToRun",
        "physical_print_verified = $true",
        "Delete-PrintJob",
    ):
        assert forbidden not in src
    assert "No resubmission" in src
