from datetime import date
import subprocess

import pytest

from kushluk import printing
from kushluk.models import PracticalItem, Story
from kushluk.print_profiles import impose_a3_folded, validate_a3_booklet
from kushluk.printing import PrinterCapabilities, print_pdf
from kushluk.publication import build_publication
from kushluk.renderer import render_html, render_pdf


def test_a3_folded_contains_outside_4_1_and_inside_2_3(tmp_path):
    pytest.importorskip("weasyprint")
    pypdf = pytest.importorskip("pypdf")
    publication = build_publication(
        target_date=date(2026, 9, 23), timezone="Europe/Berlin",
        location_name="Cologne",
        practical=[PracticalItem("Morning", "08:00")],
        stories=[Story(str(i), f"Story {i}", "Summary.", "Publisher") for i in range(3)],
    )
    source = render_pdf(
        render_html(publication, tmp_path / "original.html"), tmp_path / "original.pdf"
    )
    original_bytes = source.read_bytes()
    output = impose_a3_folded(source, tmp_path / "booklet.pdf")
    reader = pypdf.PdfReader(str(output))
    assert len(reader.pages) == 2
    assert validate_a3_booklet(output) == []
    assert source.read_bytes() == original_bytes
    for side, pair in enumerate(((4, 1), (2, 3))):
        text = " ".join(reader.pages[side].extract_text().split())
        for logical in pair:
            assert f"{logical} / 4" in text


def test_a3_rejects_unvalidated_source(tmp_path):
    pytest.importorskip("pypdf")
    pypdf = pytest.importorskip("pypdf")
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=595, height=842)
    source = tmp_path / "one-page.pdf"
    with source.open("wb") as stream:
        writer.write(stream)
    with pytest.raises(ValueError, match="unvalidated"):
        impose_a3_folded(source, tmp_path / "booklet.pdf")
    assert not (tmp_path / "booklet.pdf").exists()


def test_a3_refuses_printer_without_confirmed_media_and_duplex(tmp_path, monkeypatch):
    pdf = tmp_path / "booklet.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(printing.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        printing, "detect_printer_capabilities",
        lambda printer: PrinterCapabilities(printer, True, True, ("A4",), "Ready"),
    )
    monkeypatch.setattr(
        printing.subprocess, "run",
        lambda *args, **kwargs: pytest.fail("No job should be submitted"),
    )
    result = print_pdf(pdf, "Test", execute=True, media="A3", require_duplex=True)
    assert not result.success
    assert "does not advertise A3" in result.detail


def test_a3_submission_uses_a3_and_short_edge_only_when_confirmed(tmp_path, monkeypatch):
    pdf = tmp_path / "booklet.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(printing.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        printing, "detect_printer_capabilities",
        lambda printer: PrinterCapabilities(printer, True, True, ("A4", "A3"), "Ready"),
    )
    commands = []

    def run(args, **kwargs):
        commands.append(args)
        return subprocess.CompletedProcess(args, 0, "request id is Test-3", "")

    monkeypatch.setattr(printing.subprocess, "run", run)
    result = print_pdf(
        pdf, "Test", execute=True, media="A3", duplex_edge="short", require_duplex=True
    )
    assert result.success and result.duplex_used
    assert "media=A3" in commands[0]
    assert "sides=two-sided-short-edge" in commands[0]
    assert str(pdf) == commands[0][-1]


def test_a3_refuses_unknown_duplex(tmp_path, monkeypatch):
    pdf = tmp_path / "booklet.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(printing.shutil, "which", lambda name: "/usr/bin/lp")
    monkeypatch.setattr(
        printing, "detect_printer_capabilities",
        lambda printer: PrinterCapabilities(printer, True, False, ("A3",), "Unknown duplex"),
    )
    result = print_pdf(pdf, "Test", execute=True, media="A3", require_duplex=True)
    assert not result.success and "duplex" in result.detail
