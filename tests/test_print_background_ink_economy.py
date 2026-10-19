"""Keep the accepted render geometry while eliminating the beige print flood.

This tests source intent only; real print behavior and aesthetics need paper evidence.
"""
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "src/kushluk/templates/edition.html"


def test_white_stock_print_profile_does_not_ink_the_paper_background():
    html = PAGE.read_text(encoding="utf-8")
    assert "--paper: #f3efe4;" in html
    assert "body { background: #ded8cc; padding: 12px; }" in html
    assert "margin: 0 auto 12px; background: var(--paper);" in html
    assert "@media print {" in html
    assert "body { background: #fff; print-color-adjust: exact;" in html
    assert ".sheet { background: #fff; }" in html
    assert ".sun { background: var(--ink); }" in html


def test_no_rejected_hierarchy_or_layout_reintroduced():
    html = PAGE.read_text(encoding="utf-8")
    assert "h1 { font-size: 32pt; line-height: .95;" in html
    assert "h2 { margin: 0 0 5mm; font-size: 24pt;" in html
    assert "article { border-top: .3mm solid var(--ink);" in html
    assert ".sheet:not(.front) h1" not in html
    assert "break-after: page;" in html
    assert "aria-label=\"Page {{ page.number }} of 4\"" in html
