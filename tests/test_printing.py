import subprocess

from kushluk import printing
from kushluk.printing import detect_printer_capabilities, parse_lpoptions, print_pdf


def test_parse_lpoptions_detects_duplex_and_media():
    sample = """
Duplex/2-Sided Printing: *None DuplexNoTumble DuplexTumble
PageSize/Media Size: *A4 Letter A5
"""
    duplex, media = parse_lpoptions(sample)
    assert duplex is True
    assert "A4" in media


def test_parse_lpoptions_handles_simplex_printer():
    sample = "PageSize/Media Size: *A4 Letter\n"
    duplex, media = parse_lpoptions(sample)
    assert duplex is False
    assert media == ("A4", "Letter")


def test_parse_lpoptions_supports_ipp_driverless_sides():
    # macOS AirPrint/IPP printers often expose 'sides' instead of legacy 'Duplex'.
    sample = (
        "sides/2-Sided Printing: *one-sided two-sided-long-edge two-sided-short-edge\n"
        "media/Media Size: *iso_a4_210x297mm na_letter_8.5x11in\n"
    )
    duplex, media = parse_lpoptions(sample)
    assert duplex is True
    assert "iso_a4_210x297mm" in media


def test_mac_cups_default_printer_and_duplex_job(tmp_path, monkeypatch):
    monkeypatch.delenv("LPDEST", raising=False)
    monkeypatch.delenv("PRINTER", raising=False)
    monkeypatch.setattr(printing.shutil, "which", lambda name: f"/usr/bin/{name}")
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        if args[0].endswith("lpstat") and args[1:] == ["-d"]:
            return subprocess.CompletedProcess(args, 0, "system default destination: Office_Printer\n", "")
        if args[0].endswith("lpoptions"):
            return subprocess.CompletedProcess(
                args, 0, "sides/2-Sided Printing: *one-sided two-sided-long-edge\n", ""
            )
        if args[0].endswith("lpstat") and args[1:3] == ["-p", "Office_Printer"]:
            return subprocess.CompletedProcess(
                args, 0, "printer Office_Printer is idle. enabled since Friday\n", ""
            )
        if args[0].endswith("lp"):
            return subprocess.CompletedProcess(args, 0, "request id is Office_Printer-27", "")
        raise AssertionError(f"Unexpected command: {args}")

    monkeypatch.setattr(printing.subprocess, "run", fake_run)
    pdf = tmp_path / "morning edition.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    capabilities = detect_printer_capabilities()
    assert capabilities.printer == "Office_Printer"
    assert capabilities.available and capabilities.duplex_supported

    result = print_pdf(pdf, execute=True)
    assert result.success and result.attempted and result.duplex_used
    assert result.printer == "Office_Printer"
    lp_command = next(args for args in calls if args[0] == "/usr/bin/lp")
    assert lp_command[1:3] == ["-d", "Office_Printer"]
    assert "sides=two-sided-long-edge" in lp_command
    assert str(pdf) == lp_command[-1]


def test_mac_cups_lp_dest_priority_and_simplex(tmp_path, monkeypatch):
    monkeypatch.setenv("LPDEST", "Personal_Printer")
    monkeypatch.setenv("PRINTER", "Ignored_Printer")
    monkeypatch.setattr(printing.shutil, "which", lambda name: f"/usr/bin/{name}")
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        if args[0].endswith("lpoptions"):
            return subprocess.CompletedProcess(
                args, 0, "Duplex/2-Sided Printing: *None DuplexNoTumble\n", ""
            )
        if args[0].endswith("lpstat"):
            return subprocess.CompletedProcess(
                args, 0, "printer Personal_Printer is idle. enabled since Friday\n", ""
            )
        return subprocess.CompletedProcess(args, 0, "request id is Personal_Printer-42", "")

    monkeypatch.setattr(printing.subprocess, "run", fake_run)
    pdf = tmp_path / "edition.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    result = print_pdf(pdf, execute=True, duplex=False)
    assert result.success and not result.duplex_used
    lp_command = next(args for args in calls if args[0] == "/usr/bin/lp")
    assert lp_command[1:3] == ["-d", "Personal_Printer"]
    assert "sides=one-sided" in lp_command
    assert all(not (args[0].endswith("lpstat") and "-d" in args) for args in calls)


def test_printer_submission_timeout_becomes_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(printing.shutil, "which", lambda name: f"/usr/bin/{name}")

    def fake_run(args, **kwargs):
        if args[0].endswith("lp"):
            raise subprocess.TimeoutExpired(cmd=args, timeout=30)
        if args[0].endswith("lpoptions"):
            return subprocess.CompletedProcess(args, 0, "PageSize/Media: *A4 Letter", "")
        return subprocess.CompletedProcess(args, 0, "printer Test is idle. enabled", "")

    monkeypatch.setattr(printing.subprocess, "run", fake_run)
    pdf = tmp_path / "edition.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    result = print_pdf(pdf, printer="Test", execute=True)
    assert not result.success and result.attempted
    assert "TimeoutExpired" in result.detail


def test_cups_stderr_and_timeout_details_do_not_escape_into_receipts(tmp_path, monkeypatch):
    secret = "PRIVATE_CUPS_QUEUE_TOKEN"
    monkeypatch.setattr(printing.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(printing, "detect_printer_capabilities",
                        lambda *args: printing.PrinterCapabilities(
                            "Synthetic", True, True, ("A4",), "Ready"))
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(printing.subprocess, "run",
                        lambda *_args, **_kw: subprocess.CompletedProcess(
                            ["lp"], 1, "", f"private queue failed: {secret}"))
    result = print_pdf(pdf, execute=True)
    assert not result.success
    assert secret not in result.detail
    assert "CUPS" in result.detail

    def timeout(_cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd=f"lp -d {secret}", timeout=30)
    monkeypatch.setattr(printing.subprocess, "run", timeout)
    result = print_pdf(pdf, execute=True)
    assert not result.success
    assert "TimeoutExpired" in result.detail
    assert secret not in result.detail


def test_letter_driverless_queue_preflight_then_submits_matching_media(tmp_path, monkeypatch):
    monkeypatch.setattr(printing.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(printing, "detect_printer_capabilities",
                        lambda printer: printing.PrinterCapabilities(
                            "TestQueue", True, True,
                            ("iso_a4_210x297mm", "na_letter_8.5x11in"), "Ready"))
    from kushluk import print_profiles
    monkeypatch.setattr(print_profiles, "validate_letter_home", lambda path: [])
    calls = []
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "request id: TestQueue-8", "")
    monkeypatch.setattr(printing.subprocess, "run", fake_run)
    path = tmp_path / "letter.pdf"
    path.write_bytes(b"%PDF-1.4\n")
    result = print_pdf(path, printer="TestQueue", execute=True, media="Letter")
    assert result.success
    assert "media=Letter" in calls[0]
    assert "sides=two-sided-long-edge" in calls[0]


def test_letter_submission_rejects_a4_only_or_unknown_queue_without_side_effect(
    tmp_path, monkeypatch,
):
    monkeypatch.setattr(printing.shutil, "which", lambda name: "/usr/bin/lp")
    monkeypatch.setattr(printing.subprocess, "run",
                        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("No CUPS job")))
    file = tmp_path / "letter.pdf"
    file.write_bytes(b"%PDF-1.4\n")
    for available, choices in [(True, ("A4",)), (False, ("Letter",)), (True, ())]:
        monkeypatch.setattr(printing, "detect_printer_capabilities",
                            lambda _p, a=available, m=choices:
                            printing.PrinterCapabilities("Test", a, True, m, "Check"))
        result = print_pdf(file, "Test", execute=True, media="Letter")
        assert not result.success
        assert result.attempted


def test_letter_pdf_geometry_mismatch_blocks_even_letter_capable_queue(
    tmp_path, monkeypatch,
):
    monkeypatch.setattr(printing.shutil, "which", lambda name: "/usr/bin/lp")
    monkeypatch.setattr(printing, "detect_printer_capabilities",
                        lambda printer: printing.PrinterCapabilities(
                            "LetterQueue", True, True, ("Letter",), "Ready"))
    from kushluk import print_profiles
    monkeypatch.setattr(print_profiles, "validate_letter_home",
                        lambda path: ["A4 source, not Letter"])
    monkeypatch.setattr(printing.subprocess, "run",
                        lambda *_a, **_kw: (_ for _ in ()).throw(
                            AssertionError("Printer must not receive wrong paper geometry")))
    path = tmp_path / "a4-source.pdf"
    path.write_bytes(b"%PDF-1.4\n")
    result = print_pdf(path, "LetterQueue", execute=True, media="Letter")
    assert not result.success
    assert "four-page Letter" in result.detail
