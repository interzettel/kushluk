"""Conservative newspaper hierarchy and material-first printing regression.

Actual PDF pagination/geometry is covered by the existing print-proof,
print-inspection and layout-comparison tests on PDF-enabled CI hosts.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "src" / "kushluk" / "templates" / "edition.html"
PROOF = ROOT / "src" / "kushluk" / "print_proof.py"


def test_warm_screen_paper_does_not_force_full_beige_ink_coverage():
    css = TEMPLATE.read_text(encoding="utf-8")
    assert "--paper: #f3efe4" in css
    assert "body { background: #fff; print-color-adjust: exact;" in css
    assert ".sheet { background: #fff; }" in css
    assert ".sun { background: var(--ink); }" in css
    assert "@media screen" in css


def test_interior_masthead_differs_from_cover_without_changing_page_ids():
    html = TEMPLATE.read_text(encoding="utf-8")
    assert ".sheet:not(.front) h1 { font-size: 19pt;" in html
    assert "h1 { font-size: 30pt;" in html
    assert 'data-page="{{ page.number }}"' in html
    assert 'aria-label="Page {{ page.number }} of 4"' in html
    assert "break-after: page;" in html
    assert "position: absolute;" in html
    assert "bottom: 0;" in html
    assert "footer { left: 12mm; right: 12mm; bottom: 12mm; }" in html
    assert "grid-template-columns: repeat(2, 1fr)" in html


def test_synthetic_proof_has_calibration_density_not_fake_live_news():
    proof = PROOF.read_text(encoding="utf-8")
    assert "Check text" in proof
    assert "Check order" in proof
    assert "proof-third-c" in proof
    assert "synthetic—not news" in proof
    assert 'notes=["This is a synthetic printer-test fixture.' in proof
    assert "Never invokes a feed" in proof
