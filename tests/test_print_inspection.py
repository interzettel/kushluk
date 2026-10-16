"""Proof reports are evidence inputs, not human visual or physical acceptance."""
import json
from pathlib import Path
import subprocess

import pytest

from kushluk.cli import main
from kushluk.print_inspection import PrintInspectionError, inspect_print_pdf
from kushluk.print_proof import make_print_proof


def _synthetic_kit(tmp_path):
    pytest.importorskip("weasyprint")
    pytest.importorskip("pypdf")
    return make_print_proof(tmp_path / "synthetic-kit")


def test_structural_and_text_geometry_evidence(tmp_path):
    kit = _synthetic_kit(tmp_path)
    report = inspect_print_pdf(Path(kit["a4"]), tmp_path / "inspection")
    assert report["profile"] == "a4-home"
    assert report["structural_errors"] == []
    assert len(report["pages"]) == 4
    assert all(p["non_whitespace_text_characters"] > 0 for p in report["pages"])
    assert report["human_visual_review_required"] is True
    assert report["physical_verified"] is False
    assert report["raster_status"] == "not_requested"
    saved = json.loads((tmp_path / "inspection" / "inspection.json").read_text())
    assert saved["pdf_sha256"] == report["pdf_sha256"]
    assert all("alerts" in p for p in saved["pages"])
    assert "OFFLINE PRINT PROOF" not in json.dumps(saved)


def test_a3_validation_report_has_two_sides(tmp_path):
    kit = _synthetic_kit(tmp_path)
    report = inspect_print_pdf(
        Path(kit["a3"]), tmp_path / "a3-inspection", profile="a3-folded"
    )
    assert len(report["pages"]) == 2
    assert report["structural_errors"] == []
    assert report["physical_verified"] is False


def test_reject_pdf_without_four_page_markers(tmp_path):
    pypdf = pytest.importorskip("pypdf")
    pdf = tmp_path / "blank.pdf"
    w = pypdf.PdfWriter()
    for _ in range(4):
        w.add_blank_page(width=595.28, height=841.89)
    with pdf.open("wb") as file:
        w.write(file)
    report = inspect_print_pdf(pdf, tmp_path / "blank-inspection")
    assert report["automated_status"] == "structurally_invalid"
    assert report["structural_errors"]
    assert report["visual_verified"] is False


def test_no_automatic_claim_when_renderer_missing(tmp_path, monkeypatch):
    kit = _synthetic_kit(tmp_path)
    monkeypatch.setattr("kushluk.print_inspection.shutil.which", lambda _x: None)
    report = inspect_print_pdf(Path(kit["a4"]), tmp_path / "no-poppler",
                               rasterize=True)
    assert report["raster_status"] == "renderer_unavailable"
    assert not report["previews"]
    assert report["human_visual_review_required"] is True


def test_raster_snapshots_are_private_and_not_marked_reviewed(tmp_path, monkeypatch):
    kit = _synthetic_kit(tmp_path)
    monkeypatch.setattr("kushluk.print_inspection.shutil.which",
                        lambda _x: "/fake/pdftoppm")

    def fake_render(args, **kwargs):
        prefix = Path(args[-1])
        for i in range(1, 5):
            (prefix.parent / f"page-{i}.png").write_bytes(
                b"\x89PNG\r\n\x1a\n" + b"synthetic-image"
            )
        return subprocess.CompletedProcess(args, returncode=0)

    monkeypatch.setattr("kushluk.print_inspection.subprocess.run", fake_render)
    report = inspect_print_pdf(Path(kit["a4"]), tmp_path / "rendered",
                               rasterize=True, dpi=96)
    assert report["raster_status"] == "snapshots_generated_not_reviewed"
    assert len(report["previews"]) == 4
    assert report["visual_verified"] is False
    assert report["physical_verified"] is False
    assert all(p["sha256"] for p in report["previews"])


def test_cli_inspection_honestly_reports_paper_still_unverified(
        tmp_path, capsys, monkeypatch):
    kit = _synthetic_kit(tmp_path)
    monkeypatch.setattr("kushluk.print_inspection.shutil.which", lambda _x: None)
    assert main([
        "inspect-print", "--pdf", kit["a4"],
        "--output-dir", str(tmp_path / "cli-inspection"), "--rasterize",
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["physical_verified"] is False
    assert result["human_visual_review_required"] is True
    assert result["raster_status"] == "renderer_unavailable"


def test_no_output_directory_overwrite(tmp_path):
    kit = _synthetic_kit(tmp_path)
    dest = tmp_path / "existing"
    dest.mkdir()
    (dest / "old.txt").write_text("operator evidence")
    with pytest.raises(PrintInspectionError, match="already exists"):
        inspect_print_pdf(Path(kit["a4"]), dest)
    assert (dest / "old.txt").read_text() == "operator evidence"
