import json

import pytest

from kushluk.print_proof import make_print_proof
from kushluk.print_profiles import validate_a3_booklet
from kushluk.validation import validate_pdf


def test_offline_print_proof_builds_a4_a3_checklist_and_manifest(tmp_path):
    pytest.importorskip("pypdf")
    pytest.importorskip("weasyprint")
    artifacts = make_print_proof(tmp_path / "calibration")
    from pathlib import Path

    a4 = Path(artifacts["a4"])
    a3 = Path(artifacts["a3"])
    assert a4.is_file() and a3.is_file()
    assert validate_pdf(a4).ok
    assert validate_a3_booklet(a3) == []
    report = json.loads(Path(artifacts["manifest"]).read_text())
    assert report["a4_logical_pages"] == 4
    assert report["a3_sheet_sides"] == 2
    assert report["physical_verified"] is False
    assert report["a3_imposition"] == ["4 | 1", "2 | 3"]
    checklist = Path(artifacts["checklist"]).read_text()
    assert "actual size" in checklist.lower()
    assert "CUPS queue" in checklist
    assert "photos" in checklist
    html = Path(artifacts["html"]).read_text()
    assert "OFFLINE PRINT PROOF" in html
    assert "FRONT / PAGE 1" in html
    assert "INSIDE / PAGE 3" in html
    assert "No live sources were fetched" in html


def test_proof_documents_do_not_claim_real_print_success(tmp_path):
    pytest.importorskip("pypdf")
    pytest.importorskip("weasyprint")
    artifacts = make_print_proof(tmp_path / "calibration")
    from pathlib import Path

    checklist = Path(artifacts["checklist"]).read_text()
    assert "Physical verified: [ ] yes" in checklist
    report = json.loads(Path(artifacts["manifest"]).read_text())
    assert report["physical_verified"] is False
