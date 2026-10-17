"""Software print-proof inspection; never a claim of physical printer acceptance.

Generates a private report with PDF structure, text anchor checks and optional
Poppler raster proofs. PNG proofs still require human visual review.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
import os
from pathlib import Path
import shutil
import subprocess

from kushluk.print_profiles import validate_a3_booklet, validate_letter_home
from kushluk.validation import validate_pdf


class PrintInspectionError(ValueError):
    """Safe error that does not disclose private source contents."""


def inspect_print_pdf(
    pdf: Path,
    output_dir: Path,
    *,
    profile: str = "a4-home",
    rasterize: bool = False,
    dpi: int = 100,
) -> dict:
    """Review PDF before printing, optionally producing one PNG per sheet/page.

    Text matrix positions are *anchors*, not reliable glyph bounding boxes.
    Raster snapshots provide a separate human inspection surface.
    """
    if profile not in {"a4-home", "letter-home", "a3-folded"}:
        raise PrintInspectionError("Unknown print profile")
    if type(dpi) is not int or not (72 <= dpi <= 180):
        raise PrintInspectionError("Raster proof DPI must be between 72 and 180")
    try:
        if not pdf.is_file() or pdf.stat().st_size > 30 * 1024 * 1024:
            raise PrintInspectionError("PDF is absent or exceeds 30 MiB")
        pdf_bytes = pdf.read_bytes()
    except OSError as exc:
        raise PrintInspectionError("Cannot access PDF") from exc
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf)
        if profile == "a4-home":
            structural = validate_pdf(pdf)
            structural_errors = list(structural.errors)
            expected = 4
        elif profile == "letter-home":
            structural_errors = validate_letter_home(pdf)
            expected = 4
        else:
            structural_errors = validate_a3_booklet(pdf)
            expected = 2
    except Exception as exc:
        raise PrintInspectionError("PDF could not be inspected") from exc

    page_reports: list[dict] = []
    for index, page in enumerate(reader.pages[:8], start=1):
        box = page.mediabox
        left, bottom = float(box.left), float(box.bottom)
        width, height = float(box.width), float(box.height)
        positions: list[tuple[float, float, float]] = []
        text_count = 0

        def visitor(text, cm, tm, _font_dict, font_size):
            nonlocal text_count
            if not text.strip():
                return
            text_count += len(text.strip())
            try:
                x = cm[0] * tm[4] + cm[2] * tm[5] + cm[4]
                y = cm[1] * tm[4] + cm[3] * tm[5] + cm[5]
                size = float(font_size)
                if all(math.isfinite(v) for v in (x, y, size)):
                    positions.append((x, y, size))
            except (TypeError, ValueError, IndexError):
                return

        try:
            page.extract_text(visitor_text=visitor)
        except Exception as exc:
            raise PrintInspectionError("Unable to inspect PDF text geometry") from exc
        margin = 5.0
        outside = sum(
            x < left - margin or x > left + width + margin
            or y < bottom - margin or y > bottom + height + margin
            for x, y, _size in positions
        )
        tiny = sum(0 < size < 6.5 for _x, _y, size in positions)
        alerts = []
        if text_count == 0:
            alerts.append("no_extractable_text")
        if outside:
            alerts.append("text_anchor_outside_media_box")
        if tiny:
            alerts.append("small_text_anchor")
        if not positions and text_count:
            alerts.append("text_positions_unavailable")
        page_reports.append({
            "index": index,
            "size_pt": [round(width, 2), round(height, 2)],
            "non_whitespace_text_characters": text_count,
            "positioned_fragments": len(positions),
            "out_of_media_box_text_anchors": outside,
            "font_fragments_below_6_5pt": tiny,
            "alerts": alerts,
        })
    if len(reader.pages) != expected:
        structural_errors.append(f"Expected {expected} PDF page(s)")
    if any(item["alerts"] for item in page_reports):
        quality = "needs_visual_review"
    elif structural_errors:
        quality = "structurally_invalid"
    else:
        quality = "automated_checks_passed_pending_visual_review"
    if structural_errors:
        quality = "structurally_invalid"

    # New, private report directory; never overwrite previous human evidence.
    try:
        output_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    except FileExistsError as exc:
        raise PrintInspectionError("Proof directory already exists; choose a new directory") from exc
    previews: list[dict] = []
    raster_status = "not_requested"
    if rasterize:
        executable = shutil.which("pdftoppm")
        if not executable:
            raster_status = "renderer_unavailable"
        else:
            prefix = output_dir / "page"
            try:
                result = subprocess.run(
                    [executable, "-f", "1", "-l", str(expected),
                     "-png", "-r", str(dpi), str(pdf), str(prefix)],
                    capture_output=True, text=True, check=False, timeout=60,
                )
                if result.returncode != 0:
                    raster_status = "renderer_failed"
                else:
                    pages = sorted(output_dir.glob("page-*.png"))
                    if len(pages) != expected or any(
                        not page.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
                        for page in pages
                    ):
                        raster_status = "invalid_raster_output"
                    else:
                        raster_status = "snapshots_generated_not_reviewed"
                        for page in pages:
                            page.chmod(0o600)
                            previews.append({
                                "file": page.name,
                                "sha256": sha256(page.read_bytes()).hexdigest(),
                            })
            except (OSError, subprocess.TimeoutExpired):
                raster_status = "renderer_failed"

    report = {
        "schema_version": 1,
        "profile": profile,
        "pdf_sha256": sha256(pdf_bytes).hexdigest(),
        "automated_status": quality,
        "structural_errors": structural_errors,
        "pages": page_reports,
        "raster_status": raster_status,
        "previews": previews,
        "visual_verified": False,
        "physical_verified": False,
        "human_visual_review_required": True,
        "inspection_limitations": [
            "Text anchors are not glyph outlines: overlaps, clipped letters and image crops "
            "require inspecting raster previews.",
            "A successful PDF raster does not prove real paper, driver duplex or fold alignment.",
        ],
    }
    path = output_dir / "inspection.json"
    with os.fdopen(os.open(path, os.O_CREAT | os.O_WRONLY | os.O_EXCL, 0o600),
                   "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
        file.write("\n")
    return report
