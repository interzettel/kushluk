"""Offline A4/A3 physical-print verification fixtures; generation never submits a job."""
from __future__ import annotations

from datetime import date
from hashlib import sha256
import json
from pathlib import Path

from kushluk.models import PracticalItem, Story
from kushluk.print_profiles import impose_a3_folded, impose_letter_home
from kushluk.publication import build_publication
from kushluk.renderer import render_html, render_pdf
from kushluk.validation import validate_pdf


def make_print_proof(output_dir: Path) -> dict[str, str]:
    """Create reproducible synthetic documents with visible page identities.

    Produces four ordered A4 pages and a two-side landscape A3 folded booklet.
    Never invokes a feed, private connector, SMTP, print queue, or system printer.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    publication = build_publication(
        target_date=date(2026, 10, 17),
        timezone="Europe/Berlin",
        location_name="OFFLINE PRINT PROOF — NOT NEWS",
        practical=[
            PracticalItem("Check A4", "A4 page 1", "Front of the first sheet"),
            PracticalItem("Check contrast", "Black text", "Should remain readable"),
            PracticalItem("Check margins", "No clipping", "Inspect each paper edge"),
            PracticalItem("Check duplex", "A4 page 2", "Turn the first sheet over"),
            PracticalItem("Check text", "Small type", "Read the source and page identifiers at normal distance"),
            PracticalItem("Check order", "1 → 2 → 3 → 4", "Numbered pages must stay in sequence"),
        ],
        stories=[
            Story(
                id="proof-front", headline="FRONT / PAGE 1",
                deck="This is a synthetic four-page print verification edition. "
                     "Look for the page number at the bottom-right.",
                source_name="Kushluk offline calibration",
            ),
            Story(
                id="proof-third-a", headline="INSIDE / PAGE 3",
                deck="Check alignment and reading order after folding the A3 sheet.",
                source_name="Kushluk offline calibration",
            ),
            Story(
                id="proof-third-b", headline="SOURCE INDEX ON PAGE 4",
                deck="The opposite face is the back cover of the folded edition.",
                source_name="Kushluk offline calibration",
            ),
            Story(
                id="proof-third-c", headline="PRINT LEGIBILITY / TYPOGRAPHY",
                deck="One more article tests a denser reading page, thin rules, long labels, "
                     "and the text rhythm at actual print size. It is synthetic—not news.",
                source_name="Kushluk offline calibration",
            ),
        ],
        notes=["This is a synthetic printer-test fixture. No live sources were fetched."],
    )
    html = render_html(publication, output_dir / "kushluk-proof.html")
    a4 = render_pdf(html, output_dir / "kushluk-proof-a4.pdf")
    checked = validate_pdf(a4)
    if not checked.ok:
        raise ValueError("Invalid synthetic A4 proof: " + "; ".join(checked.errors))
    letter = impose_letter_home(a4, output_dir / "kushluk-proof-letter.pdf")
    a3 = impose_a3_folded(a4, output_dir / "kushluk-proof-a3.pdf")
    report = {
        "format": "kushluk-physical-proof-v1",
        "fixture": "synthetic, offline, no printer submission",
        "a4_file": a4.name,
        "a4_sha256": sha256(a4.read_bytes()).hexdigest(),
        "a4_logical_pages": 4,
        "letter_file": letter.name,
        "letter_sha256": sha256(letter.read_bytes()).hexdigest(),
        "letter_logical_pages": 4,
        "letter_media_box_pt": [612, 792],
        "a3_file": a3.name,
        "a3_sha256": sha256(a3.read_bytes()).hexdigest(),
        "a3_sheet_sides": 2,
        "a3_imposition": ["4 | 1", "2 | 3"],
        "physical_verified": False,
    }
    (output_dir / "kushluk-proof.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "PRINT-CHECKLIST.md").write_text(
        "# Kushluk physical print verification\n\n"
        "These files were generated without submitting any print job.\n"
        "A passed software validator does NOT verify paper output.\n\n"
        "## A4 (home printer)\n\n"
        "- [ ] Use paper size A4, actual size / 100% scaling (no 'fit to page').\n"
        "- [ ] Print four logical pages in order; duplex long-edge if supported.\n"
        "- [ ] Confirm pages 1/2 share a sheet, pages 3/4 share a sheet.\n"
        "- [ ] If simplex, verify four numbered sheets, 1 through 4.\n"
        "- [ ] Confirm no clipping, acceptable contrast, readable footer and margins.\n\n"
        "## US Letter (home printer)\n\n"
        "- [ ] Use Letter 8.5 × 11 in and print at 100% (disable automatic fit).\n"
        "- [ ] Confirm all four pages on Letter paper, long-edge duplex if supported.\n"
        "- [ ] Check printable margins, no clipping and readable page footers.\n\n"
        "## A3 (folded)\n\n"
        "- [ ] Use actual A3 landscape; duplex short-edge is initial software choice.\n"
        "- [ ] Check outside: page 4 on the left, page 1 on the right.\n"
        "- [ ] Check inside: page 2 on the left, page 3 on the right.\n"
        "- [ ] Fold at the centre; read cover > 2 > 3 > 4 in order.\n"
        "- [ ] Check reverse-side orientation; printer may require a different flip setting.\n"
        "- [ ] Check fold/binding safety, correct scaling, no clipping and legibility.\n\n"
        "## Evidence to record on #13\n\n"
        "- Printer model/firmware, OS, CUPS queue, paper stock/weight.\n"
        "- Media/duplex settings, physical photos, observed defects.\n"
        "- PDF SHA-256 from kushluk-proof.json (ties evidence to this fixture).\n"
        "- Date, operator, observations and final result.\n\n"
        "Physical verified: [ ] yes  [ ] no / pending\n",
        encoding="utf-8",
    )
    return {key: str(output_dir / value) for key, value in {
        "a4": a4.name, "letter": letter.name, "a3": a3.name, "html": html.name,
        "manifest": "kushluk-proof.json", "checklist": "PRINT-CHECKLIST.md",
    }.items()}
